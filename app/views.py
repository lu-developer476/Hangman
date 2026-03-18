import random
import string
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from .words import WORDS

MAX_ERRORS = 6
SESSION_KEY = 'hangman_state'


def _create_state():
    item = random.choice(WORDS)
    return {
        'word': item['word'].lower(),
        'hint': item['hint'],
        'guessed': [],
        'wrong': [],
        'status': 'playing',
        'message': 'Nueva partida. No la arruines en el primer intento.',
    }


def _get_state(request):
    state = request.session.get(SESSION_KEY)
    if not state:
        state = _create_state()
        request.session[SESSION_KEY] = state
    return state


def _masked_word(word, guessed):
    return ' '.join(letter if letter in guessed else '_' for letter in word)


def _build_context(state):
    guessed = set(state['guessed'])
    wrong = state['wrong']
    word = state['word']
    unique_letters = {char for char in word if char in string.ascii_lowercase}
    solved = unique_letters.issubset(guessed)
    lost = len(wrong) >= MAX_ERRORS
    status = state.get('status', 'playing')

    if solved:
        status = 'won'
    elif lost:
        status = 'lost'

    state['status'] = status

    alphabet = []
    for letter in string.ascii_lowercase:
        if letter in guessed:
            alphabet.append({'letter': letter, 'state': 'hit'})
        elif letter in wrong:
            alphabet.append({'letter': letter, 'state': 'miss'})
        else:
            alphabet.append({'letter': letter, 'state': 'idle'})

    return {
        'masked_word': _masked_word(word, guessed),
        'hint': state['hint'],
        'wrong_letters': ', '.join(wrong) if wrong else 'Ninguna todavía.',
        'errors': len(wrong),
        'max_errors': MAX_ERRORS,
        'message': state.get('message', ''),
        'status': status,
        'word': word,
        'alphabet': alphabet,
        'progress_percent': int((len(guessed & unique_letters) / len(unique_letters)) * 100) if unique_letters else 0,
        'hangman_steps': list(range(len(wrong))),
    }


@require_GET
def index(request):
    state = _get_state(request)
    context = _build_context(state)
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
    letter = request.POST.get('letter', '').strip().lower()

    if state.get('status') in {'won', 'lost'}:
        state['message'] = 'La partida terminó. Reiniciá y dejá de discutir con el destino.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if len(letter) != 1 or letter not in string.ascii_lowercase:
        state['message'] = 'Ingresá una sola letra válida de la a a la z.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if letter in state['guessed'] or letter in state['wrong']:
        state['message'] = f'La letra “{letter}” ya fue usada. No cobres doble por el mismo error.'
        request.session[SESSION_KEY] = state
        return redirect('index')

    if letter in state['word']:
        state['guessed'].append(letter)
        state['message'] = f'Bien. La letra “{letter}” sí estaba.'
    else:
        state['wrong'].append(letter)
        state['message'] = f'Nope. La letra “{letter}” no aparece por ningún lado.'

    request.session[SESSION_KEY] = state
    return redirect('index')


@require_GET
def health(request):
    return HttpResponse('ok', content_type='text/plain')
