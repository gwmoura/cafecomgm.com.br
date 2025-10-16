import time

def loading_animation(stop_event):
    chars = ['|', '/', '-', '\\']
    idx = 0
    print('⏳ Gerando conteúdo da IA ', end='', flush=True)
    while not stop_event.is_set():
        print(chars[idx % len(chars)], end='\r', flush=True)
        idx += 1
        time.sleep(0.2)
    print(' ' * 30, end='\r')  # Limpa linha