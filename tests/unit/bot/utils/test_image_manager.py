from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    'category, subfolder, expected_count',
    [
        ('existing', 'existing_folder', 3),
        ('empty', 'empty_folder', 0),
        ('nonexistent', 'nonexistent_folder', 0),
    ],
)
def test_load_category(tmp_path, image_manager, category, subfolder, expected_count):
    if subfolder == 'existing_folder':
        folder = tmp_path / 'var' / 'storage' / 'uploads' / subfolder
        folder.mkdir(parents=True)
        for i in range(3):
            (folder / f'image_{i}.jpg').touch()
    elif subfolder == 'empty_folder':
        folder = tmp_path / 'var' / 'storage' / 'uploads' / subfolder
        folder.mkdir(parents=True)

    image_manager.load_category(category, subfolder)

    assert len(image_manager.categories.get(category, [])) == expected_count


def test_add_image(image_manager, test_image):
    image_manager.add_image('test', test_image)

    assert test_image in image_manager.categories['test']


def test_add_nonexistent_image(image_manager, tmp_path):
    bad_image = tmp_path / 'nonexistend.jpg'
    image_manager.add_image('test', bad_image)

    assert 'test' not in image_manager.categories or not image_manager.categories['test']


def test_add_unsopported_format(image_manager, tmp_path):
    bad_image = tmp_path / 'test.txt'
    bad_image.touch()
    image_manager.add_image('test', bad_image)

    assert 'test' not in image_manager.categories or not image_manager.categories['test']


@pytest.mark.parametrize(
    'category, expected_result',
    [
        ('existing', True),
        ('empty', False),
        ('missing', False),
    ],
)
def test_get_random_image(image_manager, test_image, category, expected_result):
    if category == 'existing':
        image_manager.add_image('existing', test_image)

    result = image_manager.get_random_image(category)

    assert (result is not None) == expected_result


def test_get_random_image_from_empty_category(image_manager):
    image_manager.categories['empty'] = []

    assert image_manager.get_random_image('empty') is None


@patch('bot.utils.image_manager.choice')
def test_get_random_image_uses_random_choice(mock_choice, image_manager, test_image):
    mock_choice.return_value = test_image
    image_manager.add_image('test', test_image)

    result = image_manager.get_random_image('test')

    mock_choice.assert_called_once_with([test_image])
    assert result is not None
