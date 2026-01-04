project('linux-soundboard',
  version: '0.1.0',
  meson_version: '>= 0.59.0',
)

python = import('python').find_installation('python3')

# Install python files
install_subdir('model', install_dir: python.get_install_dir() / 'soundboard')
install_subdir('service', install_dir: python.get_install_dir() / 'soundboard')
install_subdir('views', install_dir: python.get_install_dir() / 'soundboard')

install_data('main.py', install_dir: python.get_install_dir() / 'soundboard')

# Wrapper script
conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('PYTHONDIR', python.get_install_dir() / 'soundboard')

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
install_data('icon.jpg',
  rename: 'com.uubroot.Soundboard.jpg',
  install_dir: get_option('datadir') / 'icons/hicolor/scalable/apps'
)
