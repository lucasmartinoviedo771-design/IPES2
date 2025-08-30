from datetime import time

GRILLAS = {
    "manana": {
        "start": time(7,45), "end": time(12,45),
        "breaks": [(time(9,5), time(9,15)), (time(10,35), time(10,45))],
    },
    "tarde": {
        "start": time(13,0), "end": time(18,0),
        "breaks": [(time(14,20), time(14,30)), (time(15,50), time(16,0))],
    },
    "vespertino": {
        "start": time(18,10), "end": time(23,10),
        "breaks": [(time(19,30), time(19,40)), (time(21,0), time(21,10))],
    },
    "sabado": {
        "start": time(9,0), "end": time(14,0),
        "breaks": [(time(10,20), time(10,30)), (time(11,50), time(12,0))],
    },
}

BLOCK_MIN = 40

def mins(t: time) -> int: return t.hour*60 + t.minute

def es_multiplo_40(t: time) -> bool:
    return mins(t) % BLOCK_MIN in (mins(GRILLAS["manana"]["start"]) % BLOCK_MIN, 0)

def atraviesa_recreo(turno: str, inicio: time, fin: time) -> bool:
    for a,b in GRILLAS[turno]["breaks"]:
        if (inicio < b and fin > a):
            # se superpone con el recreo
            return True
    return False

def dentro_de_jornada(turno: str, inicio: time, fin: time) -> bool:
    s, e = GRILLAS[turno]["start"], GRILLAS[turno]["end"]
    return (inicio >= s) and (fin <= e)
