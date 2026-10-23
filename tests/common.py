import json
from pathlib import Path
from src.triangle import hand_results, triangle_model


def hand():
    t=json.loads((Path(__file__).resolve().parents[1]/'team_config.json').read_text())['triangle']
    return hand_results(t['costs'],t.get('prices'),t.get('alternative_prices'))
