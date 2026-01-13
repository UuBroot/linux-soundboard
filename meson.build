project('linux-soundboard',
  version: '0.1.0',
  meson_version: '>= 0.59.0',
)

python = import('python').find_installation('python3')

# Use a fixed relative path for AppImage compatibility
pythondir = get_option('prefix') / 'lib' / 'soundboard'

# Install python files
install_subdir('model', install_dir: pythondir)
install_subdir('service', install_dir: pythondir)
install_subdir('views', install_dir: pythondir)

install_data('main.py', install_dir: pythondir)

# Wrapper script
conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('PYTHONDIR', pythondir)

configure_file(
  input: 'com.uubroot.Soundboard.in',
  output: 'com.uubroot.Soundboard',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

# Desktop file
install_data('com.uubroot.Soundboard.desktop',
  install_dir: get_option('datadir') / 'applications'
)

# Metainfo
install_data('com.uubroot.Soundboard.metainfo.xml',
  install_dir: get_option('datadir') / 'metainfo'
)

# Icon
install_data('icon.png',
  rename: 'com.uubroot.Soundboard.png',
  install_dir: get_option('datadir') / 'icons/hicolor/256x256/apps'
)