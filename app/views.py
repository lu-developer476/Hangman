import random
import unicodedata

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_safe

from .words import WORDS

MAX_ERRORS = 8
DIFFICULTY_CONFIG = {
    'normal': {
        'label': 'Normal',
        'helps': 1,
        'min_length': 0,
        'message': 'Nueva partida normal. Tenés 1 ayuda disponible.',
    },
    'dificil': {
        'label': 'Difícil',
        'helps': 2,
        'min_length': 8,
        'message': 'Nueva partida difícil. Palabra larga y 2 ayudas disponibles.',
    },
}
DEFAULT_DIFFICULTY = 'normal'
TOTAL_SCENES = 5
SESSION_KEY = 'hangman_state'
SPANISH_ALPHABET = 'abcdefghijklmnñopqrstuvwxyz'


def _normalize_char(char):
    """
    Normaliza vocales acentuadas para jugabilidad:
    á -> a
    é -> e
    í -> i
    ó -> o
    ú -> u

    Pero conserva la ñ como letra independiente.
    """
    char = char.lower()

    if char == 'ñ':
        return 'ñ'

    decomposed = unicodedata.normalize('NFD', char)
    return ''.join(
        c for c in decomposed
        if unicodedata.category(c) != 'Mn'
    )


def _get_difficulty_config(difficulty):
    return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG[DEFAULT_DIFFICULTY])


def _select_word(difficulty):
    config = _get_difficulty_config(difficulty)
    available_words = [
        item for item in WORDS
        if len(item['word']) >= config['min_length']
    ]
    return random.choice(available_words or WORDS)


def _create_state(difficulty=DEFAULT_DIFFICULTY):
    if difficulty not in DIFFICULTY_CONFIG:
        difficulty = DEFAULT_DIFFICULTY

    config = _get_difficulty_config(difficulty)
    item = _select_word(difficulty)
    return {
        'word': item['word'].lower(),
        'hint': item['hint'],
        'guessed': [],
        'wrong': [],
        'status': 'playing',
        'scene': random.randint(1, TOTAL_SCENES),
        'difficulty': difficulty,
        'difficulty_label': config['label'],
        'helps_remaining': config['helps'],
        'helps_total': config['helps'],
        'message': config['message'],
    }


def _get_state(request):
    state = request.session.get(SESSION_KEY)

    if not state:
        state = _create_state()
        request.session[SESSION_KEY] = state

    changed = False

    # Compatibilidad por si una sesión vieja no tiene scene/dificultad/ayudas
    if 'scene' not in state:
        state['scene'] = random.randint(1, TOTAL_SCENES)
        changed = True

    if 'difficulty' not in state:
        state['difficulty'] = DEFAULT_DIFFICULTY
        state['difficulty_label'] = DIFFICULTY_CONFIG[DEFAULT_DIFFICULTY]['label']
        state['helps_remaining'] = DIFFICULTY_CONFIG[DEFAULT_DIFFICULTY]['helps']
        state['helps_total'] = DIFFICULTY_CONFIG[DEFAULT_DIFFICULTY]['helps']
        changed = True

    if changed:
        request.session[SESSION_KEY] = state

    return state


def _masked_word(word, guessed):
    guessed_set = set(guessed)

    return ' '.join(
        letter if _normalize_char(letter) in guessed_set else '_'
        for letter in word
    )


def _get_unique_letters(word):
    """
    Obtiene las letras únicas que el usuario realmente necesita adivinar.
    Las vocales acentuadas cuentan como su versión sin acento.
    La ñ se mantiene separada.
    """
    unique_letters = set()

    for char in word:
        normalized = _normalize_char(char)
        if normalized in SPANISH_ALPHABET:
            unique_letters.add(normalized)

    return unique_letters


def _build_context(state):
    guessed = set(state.get('guessed', []))
    wrong = state.get('wrong', [])
    word = state['word']

    unique_letters = _get_unique_letters(word)

    solved = unique_letters.issubset(guessed)
    lost = len(wrong) >= MAX_ERRORS

    status = state.get('status', 'playing')
    if solved:
        status = 'won'
    elif lost:
        status = 'lost'
    else:
        status = 'playing'

    state['status'] = status

    alphabet = []
    for letter in SPANISH_ALPHABET:
        if letter in guessed:
            key_state = 'hit'
        elif letter in wrong:
            key_state = 'miss'
        else:
            key_state = 'idle'

        alphabet.append({
            'letter': letter.upper(),
            'value': letter,
            'state': key_state,
            'disabled': key_state != 'idle' or status != 'playing',
        })

    discovered_letters = guessed & unique_letters
    progress_percent = int(
        (len(discovered_letters) / len(unique_letters)) * 100
    ) if unique_letters else 0

    return {
        'masked_word': _masked_word(word, guessed),
        'hint': state['hint'],
        'wrong_letters': ', '.join(wrong).upper() if wrong else 'Ninguna todavía.',
        'errors': len(wrong),
        'max_errors': MAX_ERRORS,
        'remaining_attempts': max(MAX_ERRORS - len(wrong), 0),
        'message': state.get('message', ''),
        'status': status,
        'word': word,
        'word_length': len(word),
        'word_length_class': (
            'word-short' if len(word) <= 7 else
            'word-medium' if len(word) <= 10 else
            'word-long' if len(word) <= 13 else
            'word-extra-long'
        ),
        'alphabet': alphabet,
        'progress_percent': progress_percent,
        'hangman_steps': list(range(1, len(wrong) + 1)),
        'scene': state.get('scene', 1),
        'difficulty': state.get('difficulty', DEFAULT_DIFFICULTY),
        'difficulty_label': state.get(
            'difficulty_label',
            DIFFICULTY_CONFIG[DEFAULT_DIFFICULTY]['label'],
        ),
        'helps_remaining': state.get('helps_remaining', 0),
        'helps_total': state.get('helps_total', 0),
    }


@require_safe
def index(request):
    state = _get_state(request)
    context = _build_context(state)
    request.session[SESSION_KEY] = state
    return render(request, 'app/index.html', context)


@require_POST
def new_game(request):
    difficulty = request.POST.get('difficulty', DEFAULT_DIFFICULTY)
    request.session[SESSION_KEY] = _create_state(difficulty)
    return redirect('index')


@require_POST
def reset_game(request):
    request.session.pop(SESSION_KEY, None)
    return redirect('index')


@require_POST
def guess_letter(request):
    state = _get_state(request)
    raw_letter = request.POST.get('letter', '').strip().lower()
    letter = _normalize_char(raw_letter)

    if state.get('status') in {'won', 'lost'}:
        state['message'] = 'La partida terminó. Reiniciá y dejá de discutir con el destino.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if len(raw_letter) != 1 or letter not in SPANISH_ALPHABET:
        state['message'] = 'Ingresá una sola letra válida, incluyendo la ñ.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if letter in state['guessed'] or letter in state['wrong']:
        state['message'] = f'La letra “{letter.upper()}” ya fue usada. No cobres doble por el mismo error.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    word_letters = _get_unique_letters(state['word'])

    if letter in word_letters:
        state['guessed'].append(letter)
        state['message'] = f'Bien. La letra “{letter.upper()}” sí estaba.'
    else:
        state['wrong'].append(letter)
        state['message'] = f'Nope. La letra “{letter.upper()}” no aparece por ningún lado.'

    # Recalcular estado después de cada jugada
    unique_letters = _get_unique_letters(state['word'])

    guessed_set = set(state['guessed'])
    solved = unique_letters.issubset(guessed_set)
    lost = len(state['wrong']) >= MAX_ERRORS

    if solved:
        state['status'] = 'won'
        state['message'] = 'Ganaste. Un milagro estadístico 😅'
    elif lost:
        state['status'] = 'lost'
        state['message'] = f'Perdiste. La palabra era “{state["word"].upper()}”.'
    else:
        state['status'] = 'playing'

    request.session[SESSION_KEY] = state
    return redirect('index')


@require_POST
def use_help(request):
    state = _get_state(request)

    if state.get('status') in {'won', 'lost'}:
        state['message'] = 'La partida terminó. La ayuda llegó tarde, como siempre.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if state.get('helps_remaining', 0) <= 0:
        state['message'] = 'Ya usaste todas las ayudas disponibles para esta dificultad.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    pending_letters = sorted(
        _get_unique_letters(state['word']) - set(state.get('guessed', []))
    )

    if not pending_letters:
        state['message'] = 'No quedan letras por revelar. Ya está todo servido.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    revealed_letter = random.choice(pending_letters)
    state['guessed'].append(revealed_letter)
    state['helps_remaining'] -= 1
    state['message'] = f'Ayuda usada: revelamos la letra “{revealed_letter.upper()}”.'

    if _get_unique_letters(state['word']).issubset(set(state['guessed'])):
        state['status'] = 'won'
        state['message'] = 'Ganaste con un empujoncito. También cuenta 😅'

    request.session[SESSION_KEY] = state
    return redirect('index')


@require_safe
def health(request):
    return HttpResponse('ok', content_type='text/plain')
