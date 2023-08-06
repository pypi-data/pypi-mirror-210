from distutils.core import setup
setup(
  name = 'orange_utils',         # How you named your package folder (MyLib)
  packages = ['orange_utils'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'orange utils',   # Give a short description about your library
  author = 'junjun',                   # Type in your name
  author_email = '289584104@qq.com',      # Type in your E-Mail
  url = 'https://github.com/aminnewgit/OrangeKit',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/aminnewgit/OrangeKit/dist/orange_utils-0.1.tar.gz',    # I explain this later on
  keywords = ['orange', 'data class', ''],   # Keywords that define your package best
  install_requires=[],
  classifiers=[
    #  发展时期,常见的如下
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    # 开发的目标用户
    'Intended Audience :: Developers',      # Define that your audience are developers
    # 属于什么类型
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',   # Again, pick a license
    # 目标 Python 版本
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
# https://blog.csdn.net/calvinpaean/article/details/113580458
)


