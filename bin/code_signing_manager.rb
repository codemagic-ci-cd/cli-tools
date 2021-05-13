#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "optparse"
require "set"
require "tmpdir"
require "xcodeproj"


USAGE = "Usage: #{File.basename(__FILE__)} [options] -x XCODEPROJ_PATH -u USED_PROFILES_PATH -p [{...}, ...]

Example provisioning profile in JSON format:
{
  \"name\": \"Provisioning profile name\",
  \"team_id\": \"495W92GA23\",
  \"team_name\": \"Apple Developer Team Name\",
  \"bundle_id\": \"com.example.app\",
  \"specifier\": \"fde95301-1e05-49c1-982d-dfe5d8917ead\",
  \"certificate_common_name\": \"iPhone Developer\",
  \"xcode_managed\": false
}

Example: #{File.basename(__FILE__)} -x Project.xcodeproj -u used-profiles.json -p [{...}, ...]

Arguments:
"


class Log

  @verbose = false

  def self.set_verbose(verbose)
    @verbose = verbose || false
  end

  def self.info(message)
    if @verbose
      puts message
    end
  end

  def self.error(message)
    puts message
  end

end


class VariableResolver

  def initialize(build_target, build_configuration)
    @build_target = build_target
    @build_configuration = build_configuration
  end

  def resolve(source_str, target_str)
    return unless target_str
    target_str = inherit_variable(source_str, target_str)

    Variable.new(target_str).keys_and_modifiers.each do |variable, key, modifiers|
      value = resolve_from_target_or_config(key)
      value = expand_environment_variables(value, target_str)
      value = Variable.new(value).apply modifiers
      target_str = target_str.sub(variable, value)
    end

    Log.info "> Resolved variable '#{source_str}' to '#{target_str}'"
    # In case target str is still a variable look it up from xcconfig if possible
    Variable.new(target_str).keys_and_modifiers.each do |_variable, key, modifiers|
      real_path = @build_configuration&.base_configuration_reference&.real_path || 'unknown path'
      value = resolve_variable_from_xcconfig_attributes(key)
      unless value.nil?
        Log.info "Got '#{value}' for '#{target_str}' from xcconfig #{real_path}"
        target_str = Variable.new(value).apply modifiers
      end
    end
    target_str
  end

  private

  def inherit_variable(variable_name, target_str)
    if target_str.downcase != '$inherited'
      return target_str
    end

    @build_target.project.build_configurations.each do |project_build_configuration|
      if project_build_configuration.name == @build_configuration.name
        return project_build_configuration.build_settings[variable_name]
      end
    end
    nil
  end

  def resolve_variable_from_xcconfig(variable_name, build_configuration = nil)
    build_configuration = build_configuration || @build_configuration
    base_configuration_reference = build_configuration.base_configuration_reference
    if !base_configuration_reference.nil? && base_configuration_reference.real_path.exist?
      xcconfig = Xcodeproj::Config.new(base_configuration_reference.real_path)
      xcconfig.to_hash[variable_name]
    end
  end

  def resolve_variable_from_target_configs(variable_name)
    value = nil
    Log.info "Trying to find a target with the same name as PBXProj build configuration"
    @build_target.project.build_configurations.each do |project_build_configuration|
      if project_build_configuration.name == @build_configuration.name
        Log.info "Found build config on PBXProj for target #{@build_target.name}: #{project_build_configuration.name}"
        value = project_build_configuration.build_settings[variable_name] \
                || resolve_variable_from_xcconfig(variable_name, project_build_configuration)
        if value
          break
        end
      end
    end
    value || ''
  end

  def resolve_variable_from_xcconfig_attributes(variable_name)
    base_configuration_reference = @build_configuration.base_configuration_reference
    if base_configuration_reference.nil? || !base_configuration_reference.real_path.exist?
      return nil
    end

    Log.info "Checking value for '#{variable_name}' from #{base_configuration_reference.real_path}"
    xcconfig = Xcodeproj::Config.new(base_configuration_reference.real_path)
    xcconfig.attributes[variable_name]
  end

  def resolve_from_target_or_config(variable_name)
    def discard(resolved_value, original_name)
      # Return resolved variable if it does not contain recursive reference to
      # original key. Otherwise discard this value as it is recursive definition.
      if !resolved_value.nil? && !(resolved_value.include? original_name)
        resolved_value
      end
    end

    default_options = {:TARGET_NAME => @build_target.name, :CONFIGURATION => @build_configuration.name}
    value = discard(default_options[variable_name.to_sym], variable_name) \
        || discard(@build_configuration.build_settings[variable_name], variable_name) \
        || discard(resolve_variable_from_xcconfig(variable_name), variable_name) \
        || discard(resolve_variable_from_target_configs(variable_name), variable_name)
    value
  end

  def expand_environment_variables(variable_name, target_str)
    value = variable_name
    Variable.new(value).keys_and_modifiers.each do |var, _key, _modifiers|
      # "Avoid recursion for variable '#{var}' if it is already present in target string '#{target_str}'"
      unless target_str.include? var
        resolved = resolve(var, var)
        value = value.gsub(var, resolved)
      end
    end
    value
  end

end


class Variable

  ENVIRONMENT_VARIABLE_REGEX = /(\$[{(]([^})]+)[})]|\$([^\W]+))/

  def initialize(variable_value)
    @value = variable_value
  end

  def apply(modifiers)
    return unless @value

    value = @value
    modifiers.each do |modifier|
      value = case modifier
              when "identifier" then
                value.gsub(/\W/, "_")
              when "rfc1034identifier" then
                value.gsub(/[\W_]/, "-")
              when "lower" then
                value.downcase
              when "upper" then
                value.upcase
              else
                value
              end
    end
    value
  end

  # Parses environment variables from value and extracts key name and specified modifiers.
  # For example:
  #   Variable.new('$FIRST_VAR.something.${SECOND_VAR}').keys_and_modifiers
  #     => [["$FIRST_VAR", "FIRST_VAR", []], ["${SECOND_VAR}", "SECOND_VAR", []]]
  #   Variable.new('${FIRST-VAR:my-modifier}.something.$(SECOND_VAR:mod1:mod2)').keys_and_modifiers
  #     => [["${FIRST-VAR:my-modifier}", "FIRST-VAR", ["my-modifier"]], ["$(SECOND_VAR:mod1:mod2)", "SECOND_VAR", ["mod1", "mod2"]]]
  def keys_and_modifiers
    @value.scan(ENVIRONMENT_VARIABLE_REGEX).map do |match|
      cleaned_variable = match[1] || match[2]
      parts = cleaned_variable.split(":")
      key, modifiers = parts[0], parts[1..-1]
      [match[0], key, modifiers]
    end
  end

end


class CodeSigningManager

  SKIP_SIGNING_PRODUCT_TYPES = [
      "com.apple.product-type.bundle", # Product type Bundle
      "com.apple.product-type.framework", # Product type Framework
      "com.apple.product-type.bundle.ui-testing", # Product type UI test
      "com.apple.product-type.bundle.unit-test", # Product type Unit Test
  ]

  def initialize(project_path:, used_profiles_path:, profiles:)
    @project_path = project_path
    @used_profiles_json_path = used_profiles_path
    @project = Xcodeproj::Project.open(File.realpath(project_path))
    @profiles = profiles
    @used_provisioning_profiles = Hash.new
  end

  def set_code_signing_settings
    set_xcodeproj_build_settings
    begin
      @project.save
    rescue Exception => e
      Log.error "Failed to save project #{@project}"
      Log.error "Error: #{e}"
      # Do not raise error on "Consistency issue: no parent for object"
      # https://github.com/CocoaPods/Xcodeproj/issues/691
      if e.message.include? "Consistency issue: no parent for object"
        Log.info "Ignore error, this is open xcodeproj issue"
        @used_provisioning_profiles = Hash.new
      else
        raise  # Unknown error, panic
      end
    end
    save_used_provisioning_profiles
  end

  private

  def save_used_provisioning_profiles
    used_profiles = Hash.new
    @used_provisioning_profiles.each do |profile_specifier, bundle_ids|
      used_profiles[profile_specifier] = bundle_ids.to_a
    end
    File.open(@used_profiles_json_path, 'w') do |f|
      f.write(JSON.pretty_generate(used_profiles))
    end
  end

  def handle_target_dependencies(target)
    Log.info "Handling dependencies for target '#{target}'"
    if target.dependencies.length == 0
      Log.info "\tTarget #{target} has no dependencies"
      return
    end

    target.dependencies.each do |dependency|
      dependency_target = get_real_target(dependency)
      next unless dependency_target.instance_of? Xcodeproj::Project::Object::PBXNativeTarget
      product_type = dependency_target.product_type
      if SKIP_SIGNING_PRODUCT_TYPES.include? product_type
        Log.info("\t\tSetting empty code signing settings for #{product_type} dependency target #{dependency_target}")
        skip_code_signing(dependency_target)
        if dependency_target.project.path != @project.path
          Log.info "\t\tSaving remote project #{dependency_target.project.path}"
          dependency_target.project.save
        end
      else
        Log.info "\t\tSkip handling target dependency with product type: target #{product_type}"
      end
    end
  end

  def get_real_target(dependency)
    Log.info "\tDependency: #{dependency}"
    real_target = nil
    if !dependency.target.nil?
      Log.info "\t\tDependency has a target: #{dependency.target}"
      real_target = dependency.target
    elsif !dependency.target_proxy.nil?
      begin
        Log.info "\t\tDependency has a target_proxy: #{dependency.target_proxy}"
        proxied_target = dependency.target_proxy.proxied_object
        real_target = proxied_target
        if proxied_target.nil?
          Log.info "\t\tCannot modify dependency: proxied object was nil"
        end
      rescue
        Log.info "\t\tNo proxied objects found"
      end
    else
      Log.info "No dependency target nor target_proxy found for #{dependency}"
    end
    real_target
  end

  def get_bundle_id(target, build_configuration)
    bundle_id = build_configuration.build_settings["PRODUCT_BUNDLE_IDENTIFIER"]
    if not (bundle_id.nil? || bundle_id.empty?)
      Log.info "Got bundle id '#{bundle_id}' from build settings for build configuration '#{build_configuration.name}'"
    else
      bundle_id = get_cf_bundle_identifier(build_configuration, target)
      unless bundle_id
        Log.info "Failed to obtain bundle id for build_configuration '#{build_configuration.name}'"
        return ''
      end
      Log.info "Got bundle id '#{bundle_id}' from info plist for build configuration '#{build_configuration.name}'"
    end

    resolver = VariableResolver.new(target, build_configuration)
    resolver.resolve('PRODUCT_BUNDLE_IDENTIFIER', bundle_id)
  end

  def get_bundle_id_from_root_project(build_configuration_name)
    Log.info 'Attempt to obtain bundle id value from root object build configuration'
    root_configurations = @project.root_object.build_configuration_list
    unless root_configurations
      Log.info 'Did not find root configurations from project'
      return
    end
    root_configuration_settings = root_configurations.build_settings build_configuration_name
    unless root_configuration_settings
      Log.info "Did not find root configurations for configuration #{build_configuration_name}"
      return
    end
    root_configuration_settings["PRODUCT_BUNDLE_IDENTIFIER"]
  end

  def get_bundle_id_from_base_conf(build_configuration)
    base_configuration_reference = build_configuration.base_configuration_reference
    if base_configuration_reference.nil?
      return get_bundle_id_from_root_project build_configuration.name
    end
    unless File.exist?(base_configuration_reference.real_path)
      return
    end
    xcconfig = Xcodeproj::Config.new(base_configuration_reference.real_path)
    value = xcconfig.attributes["PRODUCT_BUNDLE_IDENTIFIER"]
    if value.nil?
      Log.info "Could not obtain bundle id value from base configuration reference"
    end
    value
  end

  def get_identifier_from_info_plist(build_configuration, infoplist_path)
    Log.info "Build configuration '#{build_configuration.name}' info plist path is '#{infoplist_path}'"
    infoplist_exists = File.file? infoplist_path
    unless infoplist_exists
      Log.info "Plist #{infoplist_path} does not exist"
      return nil
    end
    info_plist = Xcodeproj::Plist.read_from_path(infoplist_path)
    info_plist["CFBundleIdentifier"]
  end

  def get_cf_bundle_identifier(build_configuration, target)

    infoplist_file = build_configuration.build_settings["INFOPLIST_FILE"]
    resolver = VariableResolver.new(target, build_configuration)
    infoplist_file = resolver.resolve('INFOPLIST_FILE', infoplist_file)

    Log.info "Build configuration #{build_configuration.name} INFOPLIST_FILE is '#{infoplist_file}'"
    if !infoplist_file
      _value = get_bundle_id_from_base_conf(build_configuration)
    else
      infoplist_path = File.join(File.dirname(@project_path), infoplist_file)
      _value = get_identifier_from_info_plist(build_configuration, infoplist_path)
    end
  end

  def skip_code_signing(target)
    Log.info "Setting empty code signing settings for target: #{target}"
    target.build_configurations.each do |build_configuration|
      build_configuration.build_settings["EXPANDED_CODE_SIGN_IDENTITY"] = ""
      build_configuration.build_settings["CODE_SIGNING_REQUIRED"] = "NO"
      build_configuration.build_settings["CODE_SIGNING_ALLOWED"] = "NO"
    end
  end

  def set_build_settings(target, build_configuration, profile)
    if profile["xcode_managed"]
      set_automatic_build_settings(target, build_configuration, profile)
    else
      set_manual_build_settings(target, build_configuration, profile)
    end
  end

  def set_automatic_build_settings(target, build_configuration, profile)
    target_attributes ||= @project.root_object.attributes["TargetAttributes"] || {}
    target_attributes[target.uuid] ||= {}
    target_attributes[target.uuid]["DevelopmentTeam"] = profile["team_id"]
    target_attributes[target.uuid]["DevelopmentTeamName"] = profile["team_name"]
    target_attributes[target.uuid]["ProvisioningStyle"] = "Automatic"

    build_configuration.build_settings.delete "CODE_SIGN_STYLE"
    build_configuration.build_settings.delete "PROVISIONING_PROFILE"
    build_configuration.build_settings.delete "PROVISIONING_PROFILE_SPECIFIER"
    build_configuration.build_settings["DEVELOPMENT_TEAM"] = profile["team_id"]

    build_configuration.build_settings.each do |build_setting, _value|
      if build_setting.start_with? "CODE_SIGN_IDENTITY[sdk="
        build_configuration.build_settings.delete build_setting
      end
    end
  end

  def set_manual_build_settings(target, build_configuration, profile)
    target_attributes ||= @project.root_object.attributes["TargetAttributes"] || {}
    target_attributes[target.uuid] ||= {}
    target_attributes[target.uuid]["ProvisioningStyle"] = "Manual"
    target_attributes[target.uuid]["DevelopmentTeam"] = profile["team_id"]

    build_configuration.build_settings["DEVELOPMENT_TEAM"] = profile["team_id"]
    build_configuration.build_settings["CODE_SIGN_STYLE"] = "Manual"
    build_configuration.build_settings["PROVISIONING_PROFILE_SPECIFIER"] = profile['name']

    build_configuration.build_settings["CODE_SIGN_IDENTITY"] = profile["certificate_common_name"]
    build_configuration.build_settings.each do |build_setting, _value|
      if build_setting.start_with? "CODE_SIGN_IDENTITY[sdk="
        build_configuration.build_settings[build_setting] = profile["certificate_common_name"]
      end
    end
  end

  def set_configuration_build_settings(build_target, build_configuration)
    Log.info "\n#{'-' * 50}\n"
    bundle_id = get_bundle_id(build_target, build_configuration)
    if bundle_id.nil? || bundle_id == ''
      Log.info "No bundle id found for target '#{build_target.name}'"
      return
    end

    profile = nil
    @profiles.each do |prov_profile|
      if File.fnmatch(prov_profile["bundle_id"], bundle_id)
        profile = prov_profile
        break
      end
    end

    unless profile
      Log.info "Did not find suitable provisioning profile for target with bundle identifier '#{bundle_id}'"
      return
    end

    mark_profile_as_used(profile, build_target, build_configuration, bundle_id)
    set_build_settings(build_target, build_configuration, profile)
  end

  def mark_profile_as_used(profile, target, build_configuration, bundle_id)
    Log.info "Using profile '#{profile['name']}' (bundle id '#{profile['bundle_id']}') for"
    Log.info "\ttarget '#{target.name}'"
    Log.info "\tbuild configuration '#{build_configuration.name}'"
    Log.info "\tbundle id '#{bundle_id}'"
    Log.info "\tspecifier '#{profile['specifier']}'"

    if @used_provisioning_profiles[profile['specifier']].nil?
      @used_provisioning_profiles[profile['specifier']] = []
    end
    target_info = {
        :bundle_id => bundle_id,
        :target_name => target.name,
        :build_configuration => build_configuration.name,
        :project_name => @project.root_object.name
    }
    @used_provisioning_profiles[profile['specifier']].push target_info
  end

  def set_target_build_settings(target)
    return unless target.instance_of? Xcodeproj::Project::Object::PBXNativeTarget
    Log.info "\n#{'=' * 50}\n"

    handle_target_dependencies(target)
    if SKIP_SIGNING_PRODUCT_TYPES.include? target.product_type
      Log.info("Will use empty code signing build settings for target '#{target}'")
      skip_code_signing(target)
      return
    end

    target.build_configurations.each do |build_configuration|
      set_configuration_build_settings(target, build_configuration)
    end
  end

  def set_xcodeproj_build_settings
    @project.targets.each do |target|
      set_target_build_settings(target)
    end
  end
end


def parse_args
  options = {}
  OptionParser.new do |parser|
    parser.banner = USAGE

    parser.on("-v", "--[no-]verbose", "Enable verbose logging") do |v|
      options[:verbose] = v
    end

    xcode_project_help = 'Xcode project at XCODEPROJ_PATH for which the code signing settings will be updated. REQUIRED.'
    parser.on('-x', '--xcode-project XCODEPROJ_PATH', String, help = xcode_project_help) do |project_path|
      begin
        Xcodeproj::Project.open(File.realpath(project_path))
      rescue
        raise OptionParser::InvalidArgument.new(": '#{project_path}' is not a valid Xcode project")
      end
      options[:project_path] = project_path
    end

    used_profiles_help = 'Used profiles will be saved as JSON object to file at USED_PROFILES_PATH. REQUIRED.'
    parser.on('-u', '--used-profiles USED_PROFILES_PATH', String, help = used_profiles_help) do |used_profiles_path|
      unless used_profiles_path.end_with?('.json')
        raise OptionParser::InvalidArgument.new(": '#{used_profiles_path}' is not JSON file")
      end
      options[:used_profiles_path] = used_profiles_path
    end

    profiles_help = 'Apply code signing settings from JSON encoded list PROFILES. REQUIRED.'
    parser.on('-p', '--profiles PROFILES', String, help = profiles_help) do |profiles_json|
      begin
        profiles = JSON.parse(profiles_json)
      rescue
        raise OptionParser::InvalidArgument.new(": '#{profiles_json}' is not a valid JSON")
      end
      unless profiles.class == Array
        raise OptionParser::InvalidArgument.new(": Array expected, #{profiles.class} given")
      end
      options[:profiles] = profiles
    end
  end.parse!

  raise OptionParser::MissingArgument.new("Missing required argument --xcode-project") unless options[:project_path]
  raise OptionParser::MissingArgument.new("Missing required argument --used-profiles") unless options[:used_profiles_path]
  raise OptionParser::MissingArgument.new("Missing required argument --profiles") unless options[:profiles]

  options
end


def main(args)
  Log.set_verbose args[:verbose]
  code_signing_manager = CodeSigningManager.new(
      project_path: args[:project_path],
      used_profiles_path: args[:used_profiles_path],
      profiles: args[:profiles])
  code_signing_manager.set_code_signing_settings
end


if __FILE__ == $0
  args = parse_args
  main(args)
end
