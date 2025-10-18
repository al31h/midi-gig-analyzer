import sys
import argparse
import re
from datetime import datetime
from bisect import bisect_left
from typing import Dict, Any, List, Optional, Tuple

# Format de date/heure utilisé dans le log
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# ==============================================================================
# FONCTIONS GENERIQUES
# ==============================================================================

def convert_hex_to_14bits(value16):
    # les valeurs MIDI sont codées sur des octets de 7 bits
    msb = int(value16 & 0x3F80) >> 7
    lsb = int(value16 & 0x7f)
    
    value14 = (msb << 8) + lsb
    
    return value14
        
# --- Mappages et Tables de Valeurs (Identiques à votre script) ---
# ... (Les tables de mapping restent ici)
CQ_MUTE_CHANNELS_MAP = {
    'IN1': 0x0000, 'IN2': 0x0001, 'IN3': 0x0002, 'IN4': 0x0003,
    'IN5': 0x0004, 'IN6': 0x0005, 'IN7': 0x0006, 'IN8': 0x0007,
    'IN9': 0x0008, 'IN10': 0x0009, 'IN11': 0x000A, 'IN12': 0x000B,
    'IN13': 0x000C, 'IN14': 0x000D, 'IN15': 0x000E, 'IN16': 0x000F,
    'ST1': 0x0018, 'ST2': 0x001A, 'USB': 0x001C, 'BT': 0x001E,
    'FX1': 0x0051, 'FX2': 0x0052, 'FX3': 0x0053, 'FX4': 0x0054,
    'MAIN': 0x0044,
    'OUT1': 0x0045, 'OUT2': 0x0046, 'OUT3': 0x0047, 'OUT4': 0x0048, 'OUT5': 0x0049, 'OUT6': 0x004A,
    'MGRP1': 0x0400, 'MGRP2': 0x0401, 'MGRP3': 0x0402, 'MGRP4': 0x0403,
    'DCA1': 0x0200, 'DCA2': 0x0201, 'DCA3': 0x0202, 'DCA4': 0x0203
}
CQ_FADER_TO_MAIN_MAP = {
    'IN1': 0x4000, 'IN2': 0x4001, 'IN3': 0x4002, 'IN4': 0x4003,
    'IN5': 0x4004, 'IN6': 0x4005, 'IN7': 0x4006, 'IN8': 0x4007,
    'IN9': 0x4008, 'IN10': 0x4009, 'IN11': 0x400A, 'IN12': 0x400B,
    'IN13': 0x400C, 'IN14': 0x400D, 'IN15': 0x400E, 'IN16': 0x400F,
    'ST1': 0x4018, 'ST2': 0x401A, 'USB': 0x401C, 'BT': 0x401E,
    'FX1': 0x403C, 'FX2': 0x403D, 'FX3': 0x403E, 'FX4': 0x403F
}
CQ_FADER_TO_OUT_MAP = {
    'IN1': 0x4044, 'IN2': 0x4050, 'IN3': 0x405C, 'IN4': 0x4068,
    'IN5': 0x4074, 'IN6': 0x4100, 'IN7': 0x410C, 'IN8': 0x4118,
    'IN9': 0x4124, 'IN10': 0x4130, 'IN11': 0x413C, 'IN12': 0x4148,
    'IN13': 0x4154, 'IN14': 0x4160, 'IN15': 0x416C, 'IN16': 0x4178,
    'ST1': 0x4264, 'ST2': 0x427C, 'USB': 0x4314, 'BT': 0x432C,
    'FX1': 0x4614, 'FX2': 0x4620, 'FX3': 0x462C, 'FX4': 0x4638
}
CQ_FADER_TO_FX_MAP = {
    'IN1': 0x4C14, 'IN2': 0x4C18, 'IN3': 0x4C1C, 'IN4': 0x4C20,
    'IN5': 0x4C24, 'IN6': 0x4C28, 'IN7': 0x4C2C, 'IN8': 0x4C30,
    'IN9': 0x4C34, 'IN10': 0x4C38, 'IN11': 0x4C3C, 'IN12': 0x4C40,
    'IN13': 0x4C44, 'IN14': 0x4C48, 'IN15': 0x4C4C, 'IN16': 0x4C50,
    'ST1': 0x4C74, 'ST2': 0x4C7C, 'USB': 0x4D04, 'BT': 0x4D0C,
    'FX1': 0x4E04, 'FX2': 0x4E08, 'FX3': 0x4E0C, 'FX4': 0x4E10
}
CQ_BUS_FADER_MAP = {
    'MAIN': 0x4F00,
    'OUT1': 0x4F01, 'OUT2': 0x4F02, 'OUT3': 0x4F03, 'OUT4': 0x4F04, 'OUT5': 0x4F05, 'OUT6': 0x4F06,
    'FX1': 0x4F0D, 'FX2': 0x4F0E, 'FX3': 0x4F0F, 'FX4': 0x4F10,
    'DCA1': 0x4F20, 'DCA2': 0x4F21, 'DCA3': 0x4F22, 'DCA4': 0x4F23
}
CQ_PAN_TO_MAIN_MAP = {
    'IN1': 0x5000, 'IN2': 0x5001, 'IN3': 0x5002, 'IN4': 0x5003,
    'IN5': 0x5004, 'IN6': 0x5005, 'IN7': 0x5006, 'IN8': 0x5007,
    'IN9': 0x5008, 'IN10': 0x5009, 'IN11': 0x500A, 'IN12': 0x500B,
    'IN13': 0x500C, 'IN14': 0x500D, 'IN15': 0x500E, 'IN16': 0x500F,
    'ST1': 0x5018, 'ST2': 0x501A, 'USB': 0x501C, 'BT': 0x501E,
    'FX1': 0x503C, 'FX2': 0x503D, 'FX3': 0x503E, 'FX4': 0x503F
}
CQ_PAN_TO_OUT_MAP = {
    'IN1': 0x5044, 'IN2': 0x5050, 'IN3': 0x505C, 'IN4': 0x5068,
    'IN5': 0x5074, 'IN6': 0x5100, 'IN7': 0x510C, 'IN8': 0x5118,
    'IN9': 0x5124, 'IN10': 0x5130, 'IN11': 0x513C, 'IN12': 0x5148,
    'IN13': 0x5154, 'IN14': 0x5160, 'IN15': 0x516C, 'IN16': 0x5178,
    'ST1': 0x5264, 'ST2': 0x527C, 'USB': 0x5314, 'BT': 0x532C,
    'FX1': 0x5614, 'FX2': 0x5620, 'FX3': 0x562C, 'FX4': 0x5638
}

TABLE_VCVF_FADER_VAL14 = [
    [-89, 0x0140], [-85, 0x0200], [-80, 0x0240], [-75, 0x0300], [-70, 0x0400], [-65, 0x0500], [-60, 0x0600], [-55, 0x0700],
    [-50, 0x0800], [-45, 0x0C00], [-40, 0x0F40], [-38, 0x1240], [-36, 0x1540], [-35, 0x1700], [-34, 0x1900], [-33, 0x1A00],
    [-32, 0x1C00], [-31, 0x1D40], [-30, 0x1F00], [-29, 0x2040], [-28, 0x2200], [-27, 0x2340], [-26, 0x2500], [-25, 0x2640],
    [-24, 0x2840], [-23, 0x2A00], [-22, 0x2B40], [-21, 0x2D00], [-20, 0x2E40], [-19, 0x3000], [-18, 0x3140], [-17, 0x3300],
    [-16, 0x3440], [-15, 0x3600], [-14, 0x3800], [-13, 0x3940], [-12, 0x3B00], [-11, 0x3C40], [-10, 0x3E00], [-9, 0x4140],
    [-8, 0x4440], [-7, 0x4800], [-6, 0x4B00], [-5, 0x4E40], [-4, 0x5240], [-3, 0x5640], [-2, 0x5A00], [-1, 0x5E00],
    [0, 0x6200], [1, 0x6540], [2, 0x6900], [3, 0x6C40], [4, 0x7000], [5, 0x7340], [6, 0x7540], [7, 0x7800],
    [8, 0x7A40], [9, 0x7D00], [10, 0x7F40]
]

TABLE_VCVF_PAN_VAL14 = [
    [-100, 0x0000], [-90, 0x0633], [-80, 0x0C66], [-70, 0x1319], [-60, 0x194C], [-50, 0x1F7F], [-40, 0x2632], [-30, 0x2C65],
    [-20, 0x3318], [-15, 0x3632], [-10, 0x394B], [-5, 0x3C65], [0, 0x4000], [5, 0x4318], [10, 0x4632], [15, 0x494B],
    [20, 0x4C65], [30, 0x5318], [40, 0x594B], [50, 0x5F7F], [60, 0x6632], [70, 0x6C65], [80, 0x7318],
    [90, 0x764B], [100, 0x7F7F]
]


def reverse_map(mapping: Dict[str, int]) -> Dict[int, str]:
    return {v: k for k, v in mapping.items()}

REV_MUTE_MAP = reverse_map(CQ_MUTE_CHANNELS_MAP)
REV_FADER_TO_MAIN_MAP = reverse_map(CQ_FADER_TO_MAIN_MAP)
REV_FADER_TO_OUT_MAP = reverse_map(CQ_FADER_TO_OUT_MAP)
REV_FADER_TO_FX_MAP = reverse_map(CQ_FADER_TO_FX_MAP)
REV_BUS_FADER_MAP = reverse_map(CQ_BUS_FADER_MAP)
REV_PAN_TO_MAIN_MAP = reverse_map(CQ_PAN_TO_MAIN_MAP)
REV_PAN_TO_OUT_MAP = reverse_map(CQ_PAN_TO_OUT_MAP)

FADER_VAL14_MAP = {v: d for d, v in TABLE_VCVF_FADER_VAL14}
PAN_VAL14_MAP = {v: p for p, v in TABLE_VCVF_PAN_VAL14}

FADER_TO_OUT_BASES = sorted(CQ_FADER_TO_OUT_MAP.items(), key=lambda item: item[1])
FADER_TO_FX_BASES = sorted(CQ_FADER_TO_FX_MAP.items(), key=lambda item: item[1])
PAN_TO_OUT_BASES = sorted(CQ_PAN_TO_OUT_MAP.items(), key=lambda item: item[1])


# --- Fonctions d'Analyse (Inchangées) ---
def get_channel_name(channel_id, channel_map):
    """Trouve le nom du canal à partir de l'ID."""
    return channel_map.get(channel_id, f"Canal inconnu (0x{channel_id:04X})")

def find_base_channel_info(channel_id, base_list, max_offset):
    """Trouve le canal de base et son adresse pour les mappings contigus."""
    base_addresses = [item[1] for item in base_list]
    idx = bisect_left(base_addresses, channel_id)

    if idx == 0 and channel_id != base_addresses[0]:
        return None, None
    
    if idx < len(base_addresses) and channel_id == base_addresses[idx]:
        base_name, base_id = base_list[idx]
        return base_name, base_id
    
    base_idx = idx - 1
    if base_idx < 0:
        return None, None
        
    base_name, base_id = base_list[base_idx]
    
    if channel_id < base_id + max_offset:
        return base_name, base_id
    
    return None, None

def get_fader_aux_info(channel_id):
    channel_name, base_channel_id = find_base_channel_info(channel_id, FADER_TO_OUT_BASES, max_offset=6)
    if channel_name is not None and base_channel_id is not None:
        aux_index = channel_id - base_channel_id
        if 0 <= aux_index <= 5: 
            return channel_name, f"AUX{aux_index + 1}"
    return f"Canal inconnu Fader/Aux (0x{channel_id:04X})", "AUX Inconnu"

def get_fader_fx_info(channel_id):
    channel_name, base_channel_id = find_base_channel_info(channel_id, FADER_TO_FX_BASES, max_offset=4)
    if channel_name is not None and base_channel_id is not None:
        fx_index = channel_id - base_channel_id
        if 0 <= fx_index <= 3: 
            return channel_name, f"FX{fx_index + 1}"
    return f"Canal inconnu Fader/Fx (0x{channel_id:04X})", "FX Inconnu"

def get_pan_aux_info(channel_id):
    channel_name, base_channel_id = find_base_channel_info(channel_id, PAN_TO_OUT_BASES, max_offset=6)
    if channel_name is not None and base_channel_id is not None:
        aux_index = channel_id - base_channel_id
        if 0 <= aux_index <= 5:
            return channel_name, f"AUX{aux_index + 1}"
    return f"Canal inconnu Pan/Aux (0x{channel_id:04X})", "AUX Inconnu"

def interpolate_value(value, table_map):
    keys = sorted(table_map.keys())
    values = [table_map[k] for k in keys]
    if value <= keys[0]: return values[0]
    if value >= keys[-1]: return values[-1]
    for i in range(len(keys) - 1):
        k1, k2 = keys[i], keys[i+1]
        v1, v2 = values[i], values[i+1]
        if k1 <= value <= k2:
            if k1 == k2: return v1
            return v1 + (v2 - v1) * (value - k1) / (k2 - k1)
    return None

def decode_fader_value(value_14bit):
    if value_14bit in FADER_VAL14_MAP:
        return f"{FADER_VAL14_MAP[value_14bit]:.1f} dB"
    temp_map = {v: d for d, v in TABLE_VCVF_FADER_VAL14}
    return f"{interpolate_value(value_14bit, temp_map):.1f} dB (interpolé)"

def decode_pan_value(value_14bit):
    pan_percent = None
    if value_14bit in PAN_VAL14_MAP:
        pan_percent = PAN_VAL14_MAP[value_14bit]
    else:
        temp_map = {v: p for p, v in TABLE_VCVF_PAN_VAL14}
        pan_percent = interpolate_value(value_14bit, temp_map)
    if pan_percent is None:
        return f"Erreur de décodage Pan (0x{value_14bit:04X})"
    elif abs(pan_percent) < 0.1:
        return "center"
    elif pan_percent < 0:
        return f"left {abs(pan_percent):.1f}%"
    else:
        return f"right {abs(pan_percent):.1f}%"

def parse_midi_command(line):
    parts = line.split()
    command_type = parts[0]
    if command_type in ("Start", "Stop", "Continue", "Clock"):
        return f"MIDI {command_type}"
    elif command_type == "PC" and len(parts) >= 2:
        return f"MIDI Program Change (PC) {parts[1]}"
    elif command_type == "CC" and len(parts) >= 3:
        return f"MIDI Control Change (CC) {parts[1]} Valeur: {parts[2]}"
    elif command_type in ("Note", "Note On", "Note Off") and len(parts) >= 3:
        note_name = parts[1]
        velocity = parts[2]
        return f"MIDI {command_type} {note_name} Velocité: {velocity}"
    return f"MIDI Inconnu: {line}"


def parse_cq18t_command(chunks: List[Dict[str, Any]]) -> Tuple[str, Optional[int]]:
    """
    Analyse une commande CQ18T Chunk complète (3 ou 4 morceaux).
    Retourne l'analyse formatée et l'ID du canal (ou None).
    """
    if not chunks:
        return "Commande CQ18T incomplète/vide", None

    full_data = "".join(chunk['data'] for chunk in chunks)
    full_bytes = [int(full_data[i:i+2], 16) for i in range(0, len(full_data), 2)]
    
    if len(full_bytes) < 2 or full_bytes[0] != 0xB0 or full_bytes[1] != 0x63:
        return f"CQ18T Inconnu: Préambule invalide. Données: {full_data}", None

    if len(full_bytes) < 7:
        return f"CQ18T Inconnu: Données trop courtes. Données: {full_data}", None

    channel_high = full_bytes[2]
    channel_low = full_bytes[5]
    # L'ID du canal est codé sur 14 bits (High_byte et Low_byte).
    channel_id_raw = (channel_high << 7) | channel_low 
    channel_id = convert_hex_to_14bits(channel_id_raw) # Utilisation de la fonction restaurée.

    is_9_byte_command = False
    if len(full_bytes) >= 8:
        subtype_byte = full_bytes[7]
        is_9_byte_command = subtype_byte in (0x60, 0x61)
    elif len(full_bytes) == 9:
        is_9_byte_command = True

    if is_9_byte_command:
        if len(full_bytes) < 9:
            return f"CQ18T Inconnu: Commande 9 octets attendue, mais données incomplètes ({len(full_bytes)} octets). Données: {full_data}", None
        
        value_7bit = full_bytes[8]
        value_repr = f"0x{value_7bit:02X}"

        # MUTE
        if 0x0000 <= channel_id <= 0x0403:
            channel_name = get_channel_name(channel_id, REV_MUTE_MAP)
            state = "ON" if value_7bit == 0 else "OFF"
            return f"MUTE {channel_name} = {state} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id
        
        return f"CQ18T Inconnu (9 octets). Canal: 0x{channel_id:04X}, Valeur: {value_repr}", channel_id

    else:
        if len(full_bytes) < 12:
            return f"CQ18T Inconnu: Commande 12 octets attendue, mais données incomplètes ({len(full_bytes)} octets). Données: {full_data}", None

        value_high = full_bytes[8]
        value_low = full_bytes[11]
        
        value_14bit_raw = (value_high << 7) | value_low 
        value_14bit = convert_hex_to_14bits(value_14bit_raw) # Utilisation de la fonction restaurée.
        value_repr = f"0x{value_14bit:04X}"

        # FADER to Main
        if 0x4000 <= channel_id <= 0x403F:
            channel_name = get_channel_name(channel_id, REV_FADER_TO_MAIN_MAP)
            decoded_value = decode_fader_value(value_14bit)
            return f"Fader to Main {channel_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        # FADER to Aux (OUT)
        elif 0x4044 <= channel_id <= 0x463D:
            channel_name, aux_name = get_fader_aux_info(channel_id)
            decoded_value = decode_fader_value(value_14bit)
            if "Canal inconnu" in channel_name:
                 return f"CQ18T Inconnu (Fader/Aux). {channel_name} (Valeur: {value_repr})", channel_id
            return f"Fader {channel_name} to {aux_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        # FADER to Fx
        elif 0x4C14 <= channel_id <= 0x4E13:
            channel_name, fx_name = get_fader_fx_info(channel_id)
            decoded_value = decode_fader_value(value_14bit)
            if "Canal inconnu" in channel_name:
                 return f"CQ18T Inconnu (Fader/Fx). {channel_name} (Valeur: {value_repr})", channel_id
            return f"Fader {channel_name} to {fx_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        # Bus Fader
        elif 0x4F00 <= channel_id <= 0x4F23:
            channel_name = get_channel_name(channel_id, REV_BUS_FADER_MAP)
            decoded_value = decode_fader_value(value_14bit)
            return f"Bus Fader {channel_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        # PAN to Main
        elif 0x5000 <= channel_id <= 0x503F:
            channel_name = get_channel_name(channel_id, REV_PAN_TO_MAIN_MAP)
            decoded_value = decode_pan_value(value_14bit)
            return f"Pan to Main {channel_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        # PAN to Aux (OUT)
        elif 0x5044 <= channel_id <= 0x563C:
            channel_name, aux_name = get_pan_aux_info(channel_id)
            decoded_value = decode_pan_value(value_14bit)
            if "Canal inconnu" in channel_name:
                 return f"CQ18T Inconnu (Pan/Aux). {channel_name} (Valeur: {value_repr})", channel_id
            return f"Pan {channel_name} to {aux_name} = {decoded_value} (0x{channel_id:04X}, Valeur: {value_repr})", channel_id

        return f"CQ18T Inconnu (12 octets). Canal: 0x{channel_id:04X}, Valeur: {value_repr}", channel_id

# ==============================================================================
# NOUVELLE LOGIQUE D'ANALYSE PAR INTERVALLE
# ==============================================================================

def read_timetags(timetag_file: str) -> List[datetime]:
    """
    Lit le fichier de timetags et retourne une liste de datetimes triées.
    """
    timetags = []
    try:
        with open(timetag_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    # Assumer le format 'tag, timestamp' ou juste 'timestamp'
                    parts = line.split(',', 1)
                    ts_str = parts[1].strip() if len(parts) == 2 else line.strip()
                    
                    timetags.append(datetime.strptime(ts_str, DATETIME_FORMAT))
                except ValueError:
                    sys.stderr.write(f"Avertissement: Format de timetag invalide: {line}. Ignoré.\n")
        
        # Retourne une liste de datetimes uniques et triées
        return sorted(list(set(timetags)))
        
    except FileNotFoundError:
        sys.stderr.write(f"Erreur: Fichier de timetags '{timetag_file}' non trouvé.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Erreur lors de la lecture des timetags: {e}\n")
        sys.exit(1)


def analyze_intervals(infile: Any, outfile: Any, timetags: List[datetime]):
    """
    Extrait la dernière commande CQ18T complète pour chaque canal/interface 
    dans chaque intervalle défini par les timetags.
    """
    
    # Ajoute un timestamp maximal pour s'assurer que le dernier intervalle est traité
    timetags_with_end = timetags + [datetime.max]
    
    # Stocke la dernière commande CQ18T de chaque canal/interface: 
    # Clé: (channel_id, iface), Valeur: {'timestamp_str': ..., 'analysis': ...}
    last_command_per_channel: Dict[Tuple[int, str], Dict[str, str]] = {} 
    
    current_interval_index = 0
    cq_chunk_buffer: Dict[str, List[Dict[str, Any]]] = {'IFACE 1': [], 'IFACE 2': []}
    log_pattern = re.compile(r"^\[(IFACE\s*[12])\]\s+([\d-]+\s+[\d:.]+)\s+(.*)$")

    # Si le log commence avant le premier timetag, le premier intervalle est ignoré.
    # L'analyse commence au premier timetag.
    
    for line in infile:
        line = line.strip()
        if not line:
            continue

        match = log_pattern.match(line)
        if not match:
            continue

        iface, timestamp_str, data = match.groups()
        iface = iface.upper()
        
        try:
            timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
        except ValueError:
            continue

        # --- 1. Gestion de l'Avancement de l'Intervalle ---
        while current_interval_index < len(timetags) and timestamp >= timetags_with_end[current_interval_index]:
            
            # Écrire les résultats de l'intervalle terminé
            start_ts = timetags_with_end[current_interval_index - 1] if current_interval_index > 0 else timetags[0]
            end_ts = timetags_with_end[current_interval_index]
            
            outfile.write(f"\n--- RÉSULTATS D'INTERVALLE: {start_ts} à {end_ts} ---\n")
            
            # Tri par ID de canal pour une sortie ordonnée
            sorted_results = sorted(last_command_per_channel.items(), key=lambda item: (item[0][1], item[0][0]))
            
            for (channel_id, iface_name), result in sorted_results:
                outfile.write(f"[{iface_name}] {result['timestamp_str']} CQ18T: {result['analysis']}\n")
            
            # Réinitialisation pour le nouvel intervalle
            last_command_per_channel = {}
            current_interval_index += 1
            
            if current_interval_index >= len(timetags_with_end) - 1:
                return # Fin de l'analyse


        # Si on est avant le premier timetag, on continue de lire sans analyser
        if current_interval_index == 0 and timestamp < timetags[0]:
            continue
            
        # --- 2. Traitement des Commandes dans l'Intervalle ---

        if data.startswith("CQ18T Chunk "):
            hex_data = data.split(" ", 2)[2].replace(" ", "")
            chunk = {'timestamp': timestamp, 'data': hex_data, 'timestamp_str': timestamp_str}
            cq_chunk_buffer[iface].append(chunk)

            current_buffer = cq_chunk_buffer[iface]
            
            # Logique de complétude (version simplifiée)
            is_complete = False
            if len(current_buffer) == 3:
                if len(current_buffer[2]['data']) >= 4:
                    try:
                        byte_8 = int(current_buffer[2]['data'][2:4], 16)
                        if byte_8 in (0x60, 0x61):
                            is_complete = True
                    except ValueError:
                        pass
            if len(current_buffer) == 4:
                is_complete = True

            if is_complete:
                analysis, channel_id = parse_cq18t_command(current_buffer)
                
                # Mise à jour de la dernière valeur vue pour ce canal
                if channel_id is not None:
                    key = (channel_id, iface)
                    last_command_per_channel[key] = {
                        'timestamp_str': current_buffer[0]['timestamp_str'],
                        'analysis': analysis
                    }
                
                cq_chunk_buffer[iface] = []
                continue

            # Gestion de la désynchronisation
            if len(current_buffer) > 4:
                cq_chunk_buffer[iface] = [chunk] if chunk['data'].startswith("B063") else []

        else:
            # Réinitialisation du buffer si une commande MIDI standard interrompt un chunk CQ18T
            if cq_chunk_buffer[iface]:
                cq_chunk_buffer[iface] = []
            
            # Pas d'analyse des commandes MIDI standard dans ce mode

    # --- 3. Écriture du Dernier Intervalle (si le fichier se termine) ---
    if current_interval_index < len(timetags):
        start_ts = timetags[current_interval_index - 1] if current_interval_index > 0 else timetags[0]
        end_ts = timetags[-1] # Le dernier timetag réel
        outfile.write(f"\n--- RÉSULTATS D'INTERVALLE (Fin du log): {start_ts} à {end_ts} ---\n")
        
        sorted_results = sorted(last_command_per_channel.items(), key=lambda item: (item[0][1], item[0][0]))
        for (channel_id, iface_name), result in sorted_results:
            outfile.write(f"[{iface_name}] {result['timestamp_str']} CQ18T: {result['analysis']}\n")


# ==============================================================================
# FONCTION PRINCIPALE (analyze_log et main)
# ==============================================================================

# Rétablit analyze_log pour le mode standard
def analyze_log(infile: Any, outfile: Any, ignore_ifaces: Optional[str], start_ts_str: Optional[str], stop_ts_str: Optional[str], filter_iface: Optional[str]):
    """
    Analyse le log en mode standard (copie ou analyse complète).
    """
    
    ignore_ifaces_list = [i.strip().upper() for i in (ignore_ifaces or '').split(',') if i.strip()]
    
    start_ts = datetime.strptime(start_ts_str, DATETIME_FORMAT) if start_ts_str else None
    stop_ts = datetime.strptime(stop_ts_str, DATETIME_FORMAT) if stop_ts_str else None
    filter_iface = (filter_iface or '').upper()

    cq_chunk_buffer: Dict[str, List[Dict[str, Any]]] = { 'IFACE 1': [], 'IFACE 2': [] }
    log_pattern = re.compile(r"^\[(IFACE\s*[12])\]\s+([\d-]+\s+[\d:.]+)\s+(.*)$")

    for line in infile:
        line = line.strip()
        if not line:
            continue

        match = log_pattern.match(line)
        if not match:
            continue

        iface, timestamp_str, data = match.groups()
        iface = iface.upper()

        try:
            timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
        except ValueError:
            outfile.write(f"Ligne ignorée (timestamp invalide: {timestamp_str}): {line}\n")
            continue


        # 1. Gestion du Filtrage (copie sans analyse)
        if filter_iface:
            if iface.replace(' ', '') == filter_iface:
                if (start_ts is None or timestamp >= start_ts) and (stop_ts is None or timestamp <= stop_ts):
                    outfile.write(f"{line}\n")
            continue

        # 2. Gestion de l'Ignorance et du Temps
        if iface.replace(' ', '') in ignore_ifaces_list: 
            continue
        if start_ts is not None and timestamp < start_ts:
            continue
        if stop_ts is not None and timestamp > stop_ts:
            if cq_chunk_buffer[iface]:
                error_msg = f"Commande CQ18T incomplète (arrêt à {stop_ts_str}): {cq_chunk_buffer[iface]}"
                outfile.write(f"[{iface}] {cq_chunk_buffer[iface][0]['timestamp_str']} CQ18T Incomplet: {error_msg}\n")
                cq_chunk_buffer[iface] = []
            break

        # 3. Analyse des Données

        if data.startswith("CQ18T Chunk "):
            hex_data = data.split(" ", 2)[2].replace(" ", "")
            chunk = {'timestamp': timestamp, 'data': hex_data, 'timestamp_str': timestamp_str}
            cq_chunk_buffer[iface].append(chunk)

            current_buffer = cq_chunk_buffer[iface]
            
            is_complete = False
            if len(current_buffer) == 3:
                if len(current_buffer[2]['data']) >= 4:
                    try:
                        byte_8 = int(current_buffer[2]['data'][2:4], 16)
                        if byte_8 in (0x60, 0x61):
                            is_complete = True
                    except ValueError:
                        pass
            if len(current_buffer) == 4:
                is_complete = True

            if is_complete:
                analysis, _ = parse_cq18t_command(current_buffer)
                outfile.write(f"[{iface}] {current_buffer[0]['timestamp_str']} CQ18T: {analysis}\n")
                cq_chunk_buffer[iface] = []
                continue

            if len(current_buffer) > 4:
                error_msg = f"Commande CQ18T trop longue/désynchronisée ({len(current_buffer)} chunks). Début: {current_buffer[0]['data']}"
                outfile.write(f"[{iface}] {current_buffer[0]['timestamp_str']} CQ18T Inconnu: {error_msg}\n")
                cq_chunk_buffer[iface] = []
                if chunk['data'].startswith("B063"):
                    cq_chunk_buffer[iface].append(chunk)

        else:
            if cq_chunk_buffer[iface]:
                error_msg = f"Commande CQ18T incomplète (interrompue par {data}): {cq_chunk_buffer[iface]}"
                outfile.write(f"[{iface}] {cq_chunk_buffer[iface][0]['timestamp_str']} CQ18T Incomplet: {error_msg}\n")
                cq_chunk_buffer[iface] = []

            analysis = parse_midi_command(data)
            outfile.write(f"[{iface}] {timestamp_str} {analysis}\n")

    # Vider les buffers restants après la fin du fichier
    for iface, buffer in cq_chunk_buffer.items():
        if buffer:
            error_msg = f"Commande CQ18T incomplète (fin de fichier): {buffer}"
            outfile.write(f"[{iface}] {buffer[0]['timestamp_str']} CQ18T Incomplet: {error_msg}\n")


def main():
    parser = argparse.ArgumentParser(description="Analyse et regroupe les données d'un log MIDI/CQ18T.")
    parser.add_argument('--in', dest='input_file', default=None, help="Nom du fichier log d'entrée (par défaut: stdin).")
    parser.add_argument('--out', dest='output_file', default=None, help="Nom du fichier de sortie (par défaut: stdout).")
    parser.add_argument('--timetags', dest='timetag_file', default=None, help="Fichier contenant les timetags (un timestamp par ligne). Si fourni, active l'analyse par intervalle.")
    parser.add_argument('--ignore', dest='ignore', default=None, help="Interfaces à ignorer (ex: IFACE1,IFACE2). (Ignoré avec --timetags)")
    parser.add_argument('--start', dest='start_ts', default=None, help="Timestamp de début d'analyse. (Ignoré avec --timetags)")
    parser.add_argument('--stop', dest='stop_ts', default=None, help="Timestamp de fin d'analyse. (Ignoré avec --timetags)")
    parser.add_argument('--filter', dest='filter_iface', default=None, choices=['IFACE1', 'IFACE2', 'iface1', 'iface2'], help="Interface à filtrer. (Ignoré avec --timetags)")

    args = parser.parse_args()

    # Gestion des fichiers d'entrée/sortie
    infile = sys.stdin
    if args.input_file:
        try:
            infile = open(args.input_file, 'r')
        except FileNotFoundError:
            sys.stderr.write(f"Erreur: Fichier d'entrée '{args.input_file}' non trouvé.\n")
            sys.exit(1)
    
    outfile = sys.stdout
    if args.output_file:
        try:
            outfile = open(args.output_file, 'w')
        except Exception as e:
            sys.stderr.write(f"Erreur: Impossible d'ouvrir le fichier de sortie '{args.output_file}': {e}\n")
            sys.exit(1)

    try:
        if args.timetag_file:
            # MODE INTERVALLE
            timetags = read_timetags(args.timetag_file)
            if len(timetags) < 2:
                outfile.write("Erreur: Au moins deux timetags sont nécessaires pour définir un intervalle.\n")
                return

            analyze_intervals(infile, outfile, timetags)
            
        else:
            # MODE STANDARD
            analyze_log(
                infile, 
                outfile, 
                args.ignore, 
                args.start_ts, 
                args.stop_ts, 
                args.filter_iface
            )
    finally:
        if args.input_file:
            infile.close()
        if args.output_file:
            outfile.close()

if __name__ == "__main__":
    main()