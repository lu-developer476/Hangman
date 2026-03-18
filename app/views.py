import random
import unicodedata

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .words import WORDS

MAX_ERRORS = 8
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


def _create_state():
    item = random.choice(WORDS)
    return {
        'word': item['word'].lower(),
        'hint': item['hint'],
        'guessed': [],
        'wrong': [],
        'status': 'playing',
        'scene': random.randint(1, TOTAL_SCENES),
        'message': 'Nueva partida. No la arruines en el primer intento.',
    }


def _get_state(request):
    state = request.session.get(SESSION_KEY)

    if not state:
        state = _create_state()
        request.session[SESSION_KEY] = state

    # Compatibilidad por si una sesión vieja no tiene scene
    if 'scene' not in state:
        state['scene'] = random.randint(1, TOTAL_SCENES)
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
        'message': state.get('message', ''),
        'status': status,
        'word': word,
        'alphabet': alphabet,
        'progress_percent': progress_percent,
        'hangman_steps': list(range(1, len(wrong) + 1)),
        'scene': state.get('scene', 1),
    }


@require_GET
def index(request):
    state = _get_state(request)
    context = _build_context(state)
    request.session[SESSION_KEY] = state
    return render(request, 'app/index.html', context)


@require_POST
def new_game(request):
    request.session[SESSION_KEY] = _create_state()
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


@require_GET
def health(request):
    return HttpResponse('ok', content_type='text/plain')
