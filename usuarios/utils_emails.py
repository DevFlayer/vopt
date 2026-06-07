"""
Utilitários de envio de e-mail VOPT — Resend.
"""
import logging
import resend

logger = logging.getLogger("vopt")

def enviar_email_recuperacao(destinatario: str, link: str) -> bool:
    from django.conf import settings
    try:
        resend.api_key = settings.RESEND_API_KEY

        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [destinatario],
            "subject": "VOPT — Redefinição de senha",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 24px; background: #FAF7F2;">
              <div style="text-align: center; margin-bottom: 32px;">
                <span style="font-family: serif; font-size: 24px; letter-spacing: 0.3em; color: #0E0E0E;">VOPT</span>
              </div>
              <h2 style="font-family: serif; font-weight: 300; font-size: 28px; color: #0E0E0E; margin-bottom: 12px;">
                Redefinição de senha
              </h2>
              <p style="font-size: 14px; color: #4A4A4A; line-height: 1.6; margin-bottom: 24px;">
                Recebemos uma solicitação para redefinir a senha da sua conta VOPT.
                Clique no botão abaixo para criar uma nova senha.
              </p>
              <a href="{link}" style="display: inline-block; padding: 14px 32px; background: #0E0E0E; color: #E8D5A3; text-decoration: none; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 6px;">
                Redefinir senha
              </a>
              <p style="font-size: 12px; color: #4A4A4A; margin-top: 24px; line-height: 1.6;">
                Este link expira em <strong>30 minutos</strong>. Se você não solicitou a redefinição, ignore este e-mail.
              </p>
              <hr style="border: none; border-top: 1px solid rgba(200,169,110,0.3); margin: 32px 0;">
              <p style="font-size: 11px; color: #999; text-align: center;">
                VOPT — E-mail Profissional · Servidores no Brasil
              </p>
            </div>
            """,
        }

        resend.Emails.send(params)
        logger.info("E-mail de recuperação enviado para: %s", destinatario)
        return True
    except Exception as e:
        logger.error("Erro ao enviar e-mail: %s", str(e))
        return False