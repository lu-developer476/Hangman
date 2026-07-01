from django.test import TestCase
from django.urls import reverse

from .views import (
    MAX_ERRORS,
    SESSION_KEY,
    _get_unique_letters,
    _masked_word,
    _normalize_char,
)


class HangmanLogicTest(TestCase):
    def test_normalizes_accents_but_keeps_enye(self):
        self.assertEqual(_normalize_char('Á'), 'a')
        self.assertEqual(_normalize_char('ó'), 'o')
        self.assertEqual(_normalize_char('Ñ'), 'ñ')

    def test_unique_letters_use_playable_spanish_alphabet(self):
        self.assertEqual(_get_unique_letters('cañón'), {'c', 'a', 'ñ', 'o', 'n'})

    def test_masked_word_reveals_accented_letters_from_normalized_guess(self):
        self.assertEqual(_masked_word('teléfono', {'e', 'o'}), '_ e _ é _ o _ o')


class BasicViewsTest(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ahorcado Retro')
        self.assertContains(response, 'Vidas:')
        self.assertContains(response, 'Elegí la dificultad')
        self.assertContains(response, 'Ayuda (')
        self.assertContains(response, 'progress-track')
        self.assertContains(response, 'face dead')

    def test_health(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'ok')

    def test_wrong_guesses_advance_to_lost_state(self):
        self.client.get(reverse('index'))
        session = self.client.session
        word_letters = _get_unique_letters(session[SESSION_KEY]['word'])
        wrong_letters = [
            letter for letter in 'abcdefghijklmnñopqrstuvwxyz'
            if letter not in word_letters
        ][:MAX_ERRORS]

        self.assertEqual(len(wrong_letters), MAX_ERRORS)

        for letter in wrong_letters:
            self.client.post(reverse('guess_letter'), {'letter': letter})

        response = self.client.get(reverse('index'))
        self.assertContains(response, f'Errores: {MAX_ERRORS}/{MAX_ERRORS}')
        self.assertContains(response, 'Vidas: 0')
        self.assertContains(response, 'errors-8')
        self.assertContains(response, 'Perdiste')

    def test_new_game_accepts_difficulty_and_help_reveals_letter(self):
        self.client.post(reverse('new_game'), {'difficulty': 'dificil'})
        session = self.client.session
        state = session[SESSION_KEY]
        self.assertEqual(state['difficulty'], 'dificil')
        self.assertEqual(state['helps_remaining'], 2)
        self.assertGreaterEqual(len(state['word']), 8)

        response = self.client.post(reverse('use_help'), follow=True)
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        state = session[SESSION_KEY]
        self.assertEqual(state['helps_remaining'], 1)
        self.assertEqual(len(state['guessed']), 1)
        self.assertContains(response, 'Ayuda (1/2)')

    def test_normal_difficulty_has_one_help(self):
        self.client.post(reverse('new_game'), {'difficulty': 'normal'})
        self.assertEqual(self.client.session[SESSION_KEY]['helps_remaining'], 1)

        self.client.post(reverse('use_help'))
        self.assertEqual(self.client.session[SESSION_KEY]['helps_remaining'], 0)
