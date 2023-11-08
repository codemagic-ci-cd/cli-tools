#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "optparse"
require "set"
require "tmpdir"
require "xcodeproj"

USAGE = "Usage: #{File.basename(__FILE__)} [options] -x XCODEPROJ_PATH -r RESULT_PATH -p [{...}, ...]

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

class BundleIdentifierNotFound < StandardError
end

class VariableResolver

  ENVIRONMENT_VARIABLE_REGEX = /(\$[{(]([^})]+)[})]|\$([^\W]+))/

  def initialize(build_configuration)
    @build_configuration = build_configuration
  end

  def keys_and_modifiers(unresolved_value)
    # Parse environment variables from value and extract key name and specified modifiers.
    # For example:
    #   variable_resolver.keys_and_modifiers '$FIRST_VAR.something.${SECOND_VAR}'
    #     => [
    #          ["$FIRST_VAR", "FIRST_VAR", []],
    #          ["${SECOND_VAR}", "SECOND_VAR", []]
    #        ]
    #   variable_resolver.keys_and_modifiers '${FIRST-VAR:my-modifier}.something.$(SECOND_VAR:mod1:mod2)'
    #     => [
    #          ["${FIRST-VAR:my-modifier}", "FIRST-VAR", ["my-modifier"]],
    #          ["$(SECOND_VAR:mod1:mod2)", "SECOND_VAR", ["mod1", "mod2"]]
    #        ]
    unresolved_value.scan(ENVIRONMENT_VARIABLE_REGEX).map do |match|
      cleaned_variable = match[1] || match[2]
      parts = cleaned_variable.split(":")
      key, modifiers = parts[0], parts[1..-1]
      [match[0], key, modifiers]
    end
  end

  def apply_modifiers(value, modifiers)
    return unless value

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

  def resolve(unresolved_value)
    value = unresolved_value
    keys_and_modifiers(unresolved_value).each do |variable, key, modifiers|
      variable_value = @build_configuration.resolve_build_setting(key)
      unless variable_value.nil?
        variable_value = apply_modifiers(variable_value, modifiers)
        value = value.sub(variable, variable_value)
      end
    end

    is_resolved = value == unresolved_value
    is_resolved ? value : resolve(value)
  end
end

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

class CodeSigningManager

  APPLICATION_PRODUCT_TYPE = "com.apple.product-type.application"
  UI_TESTING_PRODUCT_TYPE = "com.apple.product-type.bundle.ui-testing"
  UNIT_TESTING_PRODUCT_TYPE = "com.apple.product-type.bundle.unit-test"

  SKIP_SIGNING_PRODUCT_TYPES = [
    "com.apple.product-type.bundle", # Product type Bundle
    "com.apple.product-type.framework", # Product type Framework
  ]

  def initialize(project_path:, result_path:, profiles:)
    @project_path = project_path
    @results_json_path = result_path
    @project = Xcodeproj::Project.open(File.realpath(project_path))
    @profiles = profiles
    @target_infos = []
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
        @target_infos = []
      else
        raise # Unknown error, panic
      end
    end
    save_use_profiles_result
  end

  private

  def save_use_profiles_result
    File.open(@results_json_path, 'w') do |f|
      f.write(JSON.pretty_generate(@target_infos))
    end
  end

  def handle_target_dependencies(target)
    Log.info "Handling dependencies for target '#{target}' of type #{target.product_type}"
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

  def get_real_target(dependency, log=true)
    Log.info "\tDependency: #{dependency}" if log
    real_target = nil
    if !dependency.target.nil?
      Log.info "\t\tDependency has a target: #{dependency.target}" if log
      real_target = dependency.target
    elsif !dependency.target_proxy.nil?
      begin
        Log.info "\t\tDependency has a target_proxy: #{dependency.target_proxy}" if log
        proxied_target = dependency.target_proxy.proxied_object
        real_target = proxied_target
        if proxied_target.nil?
          Log.info "\t\tCannot modify dependency: proxied object was nil" if log
        end
      rescue
        Log.info "\t\tNo proxied objects found" if log
      end
    else
      Log.info "No dependency target nor target_proxy found for #{dependency}" if log
    end
    real_target
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
      if build_setting.start_with?("CODE_SIGN_IDENTITY[sdk=", "PROVISIONING_PROFILE_SPECIFIER[sdk=")
        build_configuration.build_settings.delete build_setting
      end
    end
  end

  def set_manual_build_settings(target, build_configuration, profile)
    target_attributes ||= @project.root_object.attributes["TargetAttributes"] || {}
    target_attributes[target.uuid] ||= {}
    target_attributes[target.uuid]["DevelopmentTeam"] = profile["team_id"]

    build_configuration.build_settings["DEVELOPMENT_TEAM"] = profile["team_id"]
    build_configuration.build_settings["CODE_SIGN_STYLE"] = "Manual"

    # Setting provisioning profiles for unit test build targets is not allowed
    # and if done so will make the project invalid. Set profiles only in case
    # we are dealing with targets that are not unit testing targets.
    unless target.product_type == UNIT_TESTING_PRODUCT_TYPE
      target_attributes[target.uuid]["ProvisioningStyle"] = "Manual"
      build_configuration.build_settings["PROVISIONING_PROFILE_SPECIFIER"] = profile['name']
      build_configuration.build_settings.each do |build_setting, _value|
        if build_setting.start_with? "PROVISIONING_PROFILE_SPECIFIER[sdk="
          build_configuration.build_settings[build_setting] = profile["name"]
        end
      end
    end

    build_configuration.build_settings["CODE_SIGN_IDENTITY"] = profile["certificate_common_name"]
    build_configuration.build_settings.each do |build_setting, _value|
      if build_setting.start_with? "CODE_SIGN_IDENTITY[sdk="
        build_configuration.build_settings[build_setting] = profile["certificate_common_name"]
      end
    end
  end

  def get_bundle_id_from_infoplist(build_configuration)
    infoplist_file = build_configuration.resolve_build_setting('INFOPLIST_FILE')
    return nil unless infoplist_file
    infoplist_path = File.join(File.dirname(@project_path), infoplist_file)
    return nil unless File.file? infoplist_path
    begin
      info_plist = Xcodeproj::Plist.read_from_path(infoplist_path)
    rescue Exception
      return nil
    end
    unresolved_bundle_id = info_plist["CFBundleIdentifier"]
    VariableResolver.new(build_configuration).resolve(unresolved_bundle_id)
  end

  def get_build_configuration_bundle_id(build_configuration)
    def is_valid(bundle_identifier)
      not (bundle_identifier.nil? || bundle_identifier == '')
    end

    if build_configuration.nil?
      raise BundleIdentifierNotFound.new build_configuration
    end

    build_settings_bundle_id = build_configuration.resolve_build_setting("PRODUCT_BUNDLE_IDENTIFIER")
    if is_valid(build_settings_bundle_id)
      return [build_settings_bundle_id, 'build settings']
    end

    infoplist_bundle_id = get_bundle_id_from_infoplist(build_configuration)
    if is_valid(infoplist_bundle_id)
      return [infoplist_bundle_id, 'info plist file']
    end

    raise BundleIdentifierNotFound.new build_configuration
  end

  def get_host_app_target_for_unit_tests(unit_test_target)
    dependency_targets = unit_test_target.dependencies.map { |d| get_real_target(d, log=false) }
    native_dependency_targets = dependency_targets.filter { |dependency_target|
      dependency_target.instance_of? Xcodeproj::Project::Object::PBXNativeTarget
    }
    native_dependency_targets.find { |native_dependency_target|
      native_dependency_target.product_type == APPLICATION_PRODUCT_TYPE
    }
  end

  def get_app_build_configuration_for_unit_test(app_target, unit_test_build_configuration)
    app_target_build_configurations = app_target.nil? ? [] : app_target.build_configurations
    app_target_build_configurations.find { |build_configuration|
      build_configuration.name == unit_test_build_configuration.name
    }
  end

  def get_profile(bundle_id, build_configuration, build_target)
    profile = get_matching_profile(bundle_id)

    # There is no reason to have a profile for unit test build configurations.
    # However, to build for testing by targeting physical iOS devices, code
    # signing is still required and the settings, certificate information in
    # case of unit tests, come from suitable provisioning profile. Try to reuse
    # profile from the application target that unit tests target as host.
    if profile.nil? and build_target.product_type == UNIT_TESTING_PRODUCT_TYPE
      host_app_target = get_host_app_target_for_unit_tests(build_target)
      host_app_build_configuration = get_app_build_configuration_for_unit_test(host_app_target, build_configuration)
      begin
        host_application_bundle_id, _ = get_build_configuration_bundle_id(host_app_build_configuration)
      rescue BundleIdentifierNotFound
        host_application_bundle_id = nil
      end
      profile = get_matching_profile(host_application_bundle_id)
    end

    profile
  end

  def get_matching_profile(bundle_id)
    profile = nil
    @profiles.each do |prov_profile|
      if File.fnmatch(prov_profile["bundle_id"], bundle_id || '')
        profile = prov_profile
        break
      end
    end
    profile
  end

  def set_configuration_build_settings(build_target, build_configuration)
    Log.info "\n#{'-' * 50}\n"
    begin
      bundle_id, source = get_build_configuration_bundle_id(build_configuration)
    rescue BundleIdentifierNotFound
      build_config_name = build_configuration.nil? ? 'N/A' : build_configuration.name
      Log.info "No bundle id found for build configuration '#{build_config_name}'"
      return
    end

    if build_target.product_type == UI_TESTING_PRODUCT_TYPE
      # Xcode 11+ appends `.xctrunner` suffix to UI testing target bundle identifier
      # This shows an error in Xcode user interface, but is required for building
      # tests bundle for on-device testing.
      profile_bundle_id = "#{bundle_id}.xctrunner"
    else
      profile_bundle_id = bundle_id
    end

    Log.info "Resolved bundle id '#{bundle_id}' from #{source} for build configuration '#{build_configuration.name}'"
    profile = get_profile(profile_bundle_id, build_configuration, build_target)

    track_target_info(profile, build_target, build_configuration, bundle_id)
    if profile
      set_build_settings(build_target, build_configuration, profile)
    elsif build_target.product_type == UNIT_TESTING_PRODUCT_TYPE
      # In case we don't have any provisioning profile for this target,
      # that is neither the one which matches targeted host app build config
      # nor the one that directly matches unit tests target bundle identifier,
      # use empty code signing settings. This ensures that unit tests can be
      # nicely compiled for use-cases where code signing is not relevalt,
      # such as when running tests on simulator.
      skip_code_signing(build_target)
    end
  end

  def track_target_info(profile, target, build_configuration, bundle_id)
    is_unit_test_target = target.product_type == UNIT_TESTING_PRODUCT_TYPE
    profile_uuid = nil
    code_sign_identity = nil
    development_team = nil

    if profile
      profile_uuid = profile['specifier'] unless is_unit_test_target
      code_sign_identity = profile["certificate_common_name"]
      _team_name = profile["team_name"] || ""
      development_team = _team_name.empty? ? profile["team_id"] : "#{_team_name} (#{profile["team_id"]})"
    end

    target_info = {
      :bundle_id => bundle_id,
      :target_name => target.name,
      :build_configuration => build_configuration.name,
      :project_name => @project.root_object.name,
      :provisioning_profile_uuid => profile_uuid
    }

    if is_unit_test_target
      Log.info "Not using profile for unit testing target"
    elsif profile
      Log.info "Using profile '#{profile['name']}' (bundle id '#{profile['bundle_id']}') for"
    else
      Log.info "Did not find suitable provisioning profile for"
    end

    Log.info "\ttarget '#{target.name}'"
    Log.info "\tbuild configuration '#{build_configuration.name}'"
    Log.info "\tbundle id '#{bundle_id}'"
    Log.info "\tspecifier '#{profile_uuid || "N/A"}'"
    if profile.nil?
      Log.info "\tcode sign style 'N/A'"
    elsif profile["xcode_managed"]
      Log.info "\tcode sign style 'Automatic'"
    else
      Log.info "\tcode sign style 'Manual'"
      Log.info "\tcode sign identity '#{code_sign_identity || "N/A"}'"
    end
    Log.info "\tdevelopment team '#{development_team || "N/A"}'"

    unless target.product_type == UNIT_TESTING_PRODUCT_TYPE or target.product_type == UI_TESTING_PRODUCT_TYPE
      @target_infos.push(target_info)
    end
  end

  def set_target_build_settings(target)
    return unless target.instance_of? Xcodeproj::Project::Object::PBXNativeTarget
    Log.info "\n#{'=' * 50}\n"

    handle_target_dependencies(target)
    if SKIP_SIGNING_PRODUCT_TYPES.include? target.product_type
      Log.info("Will use empty code signing build settings for target '#{target}' or type #{target.product_type}")
      skip_code_signing(target)
      return
    end

    target.build_configurations.each do |build_configuration|
      set_configuration_build_settings(target, build_configuration)
    end
  end

  def set_xcodeproj_build_settings
    Log.info "\nConfigure code signing settings for project '#{@project_path}'\n"
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

    result_path_help = 'Profiles usage result will be saved as JSON object to file at RESULT_PATH. REQUIRED.'
    parser.on('-r', '--result-path RESULT_PATH', String, help = result_path_help) do |result_path|
      unless result_path.end_with?('.json')
        raise OptionParser::InvalidArgument.new(": '#{result_path}' is not JSON file")
      end
      options[:result_path] = result_path
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
  raise OptionParser::MissingArgument.new("Missing required argument --result-path") unless options[:result_path]
  raise OptionParser::MissingArgument.new("Missing required argument --profiles") unless options[:profiles]

  options
end

def main(args)
  Log.set_verbose args[:verbose]
  code_signing_manager = CodeSigningManager.new(
    project_path: args[:project_path],
    result_path: args[:result_path],
    profiles: args[:profiles])
  code_signing_manager.set_code_signing_settings
end

if __FILE__ == $0
  args = parse_args
  main(args)
end
