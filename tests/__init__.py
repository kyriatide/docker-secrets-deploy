import os, pathlib, shutil

DIR_TESTS = os.path.join(pathlib.Path(__file__).parent.absolute())

DIR_TESTS_CONFIG_SOURCE = os.path.join(DIR_TESTS, 'config.source')
DIR_TESTS_CONIFG = os.path.join(DIR_TESTS, 'config')


def setup():
    tear_down()
    os.makedirs(DIR_TESTS_CONIFG, exist_ok=True)

    # copy files
    sync_files = {os.path.join(DIR_TESTS_CONFIG_SOURCE, 'example.conf'): os.path.join(DIR_TESTS_CONIFG, 'example.conf'),
                  os.path.join(DIR_TESTS_CONFIG_SOURCE, 'example_par-abs.conf'): os.path.join(DIR_TESTS_CONIFG, 'example_par-abs.conf'),
                  os.path.join(DIR_TESTS_CONFIG_SOURCE, 'example.conf.tmpl'): os.path.join(DIR_TESTS_CONIFG, 'example.conf.tmpl')}

    for source, target in sync_files.items():
        print('Copy {} to {} ...'.format(source, target))
        shutil.copy(source, target)


def tear_down():
    if os.path.exists(DIR_TESTS_CONIFG):
        shutil.rmtree(DIR_TESTS_CONIFG)