"""
WhatsApp Cloud API — BooPixel

Script para enviar mensagens, templates e gerenciar a WhatsApp Business API.

Uso:
    python scripts/whatsapp.py send 5548999897204 "Olá, tudo bem?"
    python scripts/whatsapp.py template 5548999897204 hello_world en_US
    python scripts/whatsapp.py image 5548999897204 https://example.com/img.jpg "Legenda"
    python scripts/whatsapp.py document 5548999897204 https://example.com/doc.pdf "Proposta BooPixel"
    python scripts/whatsapp.py button 5548999897204 "Escolha um plano:" "Essential,Professional,Advanced"
    python scripts/whatsapp.py info
    python scripts/whatsapp.py templates

Variáveis de ambiente (em ~/.env):
    WHATSAPP_TOKEN           — Token permanente (System User)
    WHATSAPP_PHONE_NUMBER_ID — Phone Number ID
    WHATSAPP_WABA_ID         — WhatsApp Business Account ID
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WABA_ID = os.getenv("WHATSAPP_WABA_ID")
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def _headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }


def _post_message(payload):
    """Envia mensagem via WhatsApp Cloud API."""
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url, headers=_headers(), json=payload)
    data = response.json()

    if "error" in data:
        print(f" Erro: {data['error']['message']}")
        sys.exit(1)

    msg_id = data["messages"][0]["id"]
    wa_id = data["contacts"][0]["wa_id"]
    print(f" Mensagem enviada!")
    print(f"   Para: {wa_id}")
    print(f"   ID: {msg_id}")
    return data


def send_text(to, message):
    """Envia mensagem de texto simples."""
    print(f" Enviando texto para {to}...")
    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    })


def send_template(to, template_name, language="pt_BR", parameters=None):
    """Envia template message (pode iniciar conversa)."""
    print(f" Enviando template '{template_name}' para {to}...")
    template = {
        "name": template_name,
        "language": {"code": language},
    }
    if parameters:
        params = [{"type": "text", "text": p} for p in parameters.split(",")]
        template["components"] = [{"type": "body", "parameters": params}]

    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": template,
    })


def send_image(to, image_url, caption=None):
    """Envia imagem com legenda opcional."""
    print(f" Enviando imagem para {to}...")
    image = {"link": image_url}
    if caption:
        image["caption"] = caption
    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": image,
    })


def send_document(to, document_url, filename=None, caption=None):
    """Envia documento (PDF, DOC, etc.)."""
    print(f" Enviando documento para {to}...")
    document = {"link": document_url}
    if filename:
        document["filename"] = filename
    if caption:
        document["caption"] = caption
    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": document,
    })


def send_interactive_buttons(to, body_text, buttons_csv):
    """Envia mensagem com botões interativos (max 3)."""
    print(f" Enviando botões para {to}...")
    button_labels = [b.strip() for b in buttons_csv.split(",")][:3]
    buttons = []
    for i, label in enumerate(button_labels):
        buttons.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{i}",
                "title": label[:20],
            },
        })

    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons},
        },
    })


def send_list(to, body_text, button_text, sections_json):
    """Envia mensagem com lista de opções."""
    print(f" Enviando lista para {to}...")
    sections = json.loads(sections_json)
    return _post_message({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text,
                "sections": sections,
            },
        },
    })


def get_phone_info():
    """Mostra informações do número registrado."""
    print(" Buscando informações do número...")
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}"
    params = {
        "fields": "id,display_phone_number,verified_name,quality_rating,messaging_limit_tier,code_verification_status",
        "access_token": TOKEN,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        print(f" Erro: {data['error']['message']}")
        sys.exit(1)

    print(f"   ID:            {data.get('id')}")
    print(f"   Número:        {data.get('display_phone_number')}")
    print(f"   Nome:          {data.get('verified_name')}")
    print(f"   Qualidade:     {data.get('quality_rating', '—')}")
    print(f"   Limite msgs:   {data.get('messaging_limit_tier', '—')}")
    print(f"   Verificação:   {data.get('code_verification_status', '—')}")
    return data


def list_templates():
    """Lista todos os message templates da conta."""
    print(" Listando templates...")
    url = f"{BASE_URL}/{WABA_ID}/message_templates"
    params = {"access_token": TOKEN}
    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        print(f" Erro: {data['error']['message']}")
        sys.exit(1)

    templates = data.get("data", [])
    if not templates:
        print("   Nenhum template encontrado.")
        return data

    print(f"   {len(templates)} template(s) encontrado(s):\n")
    for t in templates:
        status_icon = "" if t["status"] == "APPROVED" else "⏳" if t["status"] == "PENDING" else ""
        print(f"   {status_icon} {t['name']}")
        print(f"      Categoria: {t['category']}")
        print(f"      Idioma:    {t['language']}")
        print(f"      Status:    {t['status']}")
        print()
    return data


def mark_as_read(message_id):
    """Marca mensagem como lida."""
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    response = requests.post(url, headers=_headers(), json=payload)
    data = response.json()
    if data.get("success"):
        print(f" Mensagem {message_id} marcada como lida.")
    else:
        print(f" Erro: {data}")
    return data


def main():
    parser = argparse.ArgumentParser(
        description="WhatsApp Cloud API — BooPixel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/whatsapp.py send 5548999897204 "Olá!"
  python scripts/whatsapp.py template 5548999897204 lead_welcome pt_BR "João"
  python scripts/whatsapp.py image 5548999897204 https://example.com/img.jpg
  python scripts/whatsapp.py document 5548999897204 https://example.com/proposta.pdf "Proposta"
  python scripts/whatsapp.py button 5548999897204 "Escolha:" "Sim,Não,Talvez"
  python scripts/whatsapp.py info
  python scripts/whatsapp.py templates
  python scripts/whatsapp.py read wamid.xxx
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando")

    # send
    p_send = subparsers.add_parser("send", help="Enviar mensagem de texto")
    p_send.add_argument("to", help="Número destino (ex: 5548999897204)")
    p_send.add_argument("message", help="Texto da mensagem")

    # template
    p_tmpl = subparsers.add_parser("template", help="Enviar template message")
    p_tmpl.add_argument("to", help="Número destino")
    p_tmpl.add_argument("name", help="Nome do template")
    p_tmpl.add_argument("language", nargs="?", default="pt_BR", help="Código idioma (default: pt_BR)")
    p_tmpl.add_argument("parameters", nargs="?", help="Parâmetros separados por vírgula")

    # image
    p_img = subparsers.add_parser("image", help="Enviar imagem")
    p_img.add_argument("to", help="Número destino")
    p_img.add_argument("url", help="URL da imagem")
    p_img.add_argument("caption", nargs="?", help="Legenda")

    # document
    p_doc = subparsers.add_parser("document", help="Enviar documento")
    p_doc.add_argument("to", help="Número destino")
    p_doc.add_argument("url", help="URL do documento")
    p_doc.add_argument("caption", nargs="?", help="Legenda/nome do arquivo")

    # button
    p_btn = subparsers.add_parser("button", help="Enviar botões interativos")
    p_btn.add_argument("to", help="Número destino")
    p_btn.add_argument("body", help="Texto da mensagem")
    p_btn.add_argument("buttons", help="Labels separados por vírgula (max 3)")

    # list
    p_list = subparsers.add_parser("list", help="Enviar lista de opções")
    p_list.add_argument("to", help="Número destino")
    p_list.add_argument("body", help="Texto da mensagem")
    p_list.add_argument("button_text", help="Texto do botão")
    p_list.add_argument("sections", help="JSON das seções")

    # info
    subparsers.add_parser("info", help="Informações do número")

    # templates
    subparsers.add_parser("templates", help="Listar templates")

    # read
    p_read = subparsers.add_parser("read", help="Marcar mensagem como lida")
    p_read.add_argument("message_id", help="ID da mensagem (wamid.xxx)")

    args = parser.parse_args()

    if not TOKEN or not PHONE_NUMBER_ID:
        print(" WHATSAPP_TOKEN e WHATSAPP_PHONE_NUMBER_ID não configurados no ~/.env")
        sys.exit(1)

    if args.command == "send":
        send_text(args.to, args.message)
    elif args.command == "template":
        send_template(args.to, args.name, args.language, args.parameters)
    elif args.command == "image":
        send_image(args.to, args.url, args.caption)
    elif args.command == "document":
        send_document(args.to, args.url, args.caption)
    elif args.command == "button":
        send_interactive_buttons(args.to, args.body, args.buttons)
    elif args.command == "list":
        send_list(args.to, args.body, args.button_text, args.sections)
    elif args.command == "info":
        get_phone_info()
    elif args.command == "templates":
        list_templates()
    elif args.command == "read":
        mark_as_read(args.message_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
