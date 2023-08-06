import re
import subprocess
from os import system
from .file_helpers import replace_line_in_file, add_to_file

def run_pipeline(path, editor):
  gemfile_path = f"{path}/Gemfile"
  application_file_path = f"{path}/config/application.rb"

  update_rails_version(gemfile_path)
  update_bootstrap_version(gemfile_path)
  add_sprockets_gem(gemfile_path)
  bundle_update()

  # run rails app:update
  system(f"THOR_MERGE={editor} bin/rails app:update")
  migrate_database()

  update_application_defaults(application_file_path)

def update_rails_version(gemfile_path):
  replace_line_in_file(
    gemfile_path, 
    re.compile('gem [\'"]rails[\'"]'), 
    "gem 'rails', '7.0.4.3'\n"
  )

def update_bootstrap_version(gemfile_path):
  replace_line_in_file(
    gemfile_path,
    re.compile('gem [\'"]bootstrap[\'"]'),
    "gem 'bootstrap', '~> 4.5'\n"
  )

def add_sprockets_gem(gemfile_path):
  add_to_file(
    gemfile_path, 
    re.compile('gem [\'"]sprockets-rails[\'"]'),
    "gem 'sprockets-rails'\n"
  )

def update_application_defaults(application_file_path):
  replace_line_in_file(
    application_file_path,
    re.compile('config.load_defaults 6\.\d'),
    "    config.load_defaults 7.0\n"
  )

def bundle_update():
  p = subprocess.Popen(['bundle', 'update'], bufsize=2048, stdin=subprocess.PIPE)
  p.wait()

  if p.returncode == 0:
    print("bundle updated")
  else:
    print("bundle update failed")

def migrate_database():
  p = subprocess.Popen(['rails', 'db:migrate'], bufsize=2048, stdin=subprocess.PIPE)
  p.wait()

  if p.returncode == 0:
    print("database migrated")
  else:
    print("database migration failed")