from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f_:
    long_description = f_.read()

def main():
    setup(name='i3a',
          description="Automatic manager for i3 tiling",
          long_description=long_description,
          long_description_content_type='text/markdown',
          use_scm_version={'write_to': 'src/i3a/_version.py'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@goral.net.pl',
          url='https://git.goral.net.pl/i3a.git',
          platforms=['linux'],
          python_requires='>=3.7,<3.10',
          setup_requires=['setuptools_scm'],
          install_requires=[
              'i3ipc==2.2.1',
          ],

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Environment :: Console',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.7',
                       'Programming Language :: Python :: 3.8',
                       'Programming Language :: Python :: 3.9',
                       'Topic :: Utilities',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},

          entry_points={
              'console_scripts': [
                    'i3a-master-stack=i3a.master_stack:main',
                    'i3a-swallow=i3a.swallow:main',
                    'i3a-move-to-empty=i3a.move_to_empty:main',
                    'i3a-swap=i3a.swap:main',
                    'i3a-resize-compass=i3a.resize_compass:main',
              ],
          },
      )

if __name__ == '__main__':
    main()

