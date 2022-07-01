import os, pathlib, shutil, glob

DIR_TESTS = os.path.join(pathlib.Path(__file__).parent.absolute())

DIR_TESTS_CONFIG_SOURCE = os.path.join(DIR_TESTS, 'config.source')
DIR_TESTS_CONIFG = os.path.join(DIR_TESTS, 'config')


def setup():
    tear_down()
    os.makedirs(DIR_TESTS_CONIFG, exist_ok=True)

    # copy files
    for source in glob.glob(os.path.join(DIR_TESTS_CONFIG_SOURCE, '*')):
        target = os.path.join(DIR_TESTS_CONIFG, os.path.basename(source))
        print('Copy {} to {} ...'.format(source, target))
        shutil.copy(source, target)


def tear_down():
    if os.path.exists(DIR_TESTS_CONIFG):
        shutil.rmtree(DIR_TESTS_CONIFG)