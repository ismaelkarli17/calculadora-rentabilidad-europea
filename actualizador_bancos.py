import json
import os
from datetime import datetime
import pytz

# Base de datos centralizada de entidades y sus condiciones
OFERTAS_BANCARIAS = [
    {
        "entidad": "Trade Republic",
        "tipo_producto": "Cuenta Remunerada",
        "tin_anual": 3.75,
        "limite_remunerado": 50000,
        "pago": "Mensual",
        "fondo_garantia": "Alemania / Irlanda (100.000 €)",
        "url_afiliado": "https://tu-enlace-de-afiliado-aqui.com"
    },
    {
        "entidad": "MyInvestor",
        "tipo_producto": "Cuenta Remunerada",
        "tin_anual": 2.50,
        "limite_remunerado": 70000,
        "pago": "Mensual",
        "fondo_garantia": "España (100.000 €)",
        "url_afiliado": "https://tu-enlace-de-afiliado-aqui.com"
    },
    {
        "entidad": "Revolut (Cuentas Flexibles)",
        "tipo_producto": "Fondo Monetario",
        "tin_anual": 3.60,
        "limite_remunerado": 100000,
        "pago": "Diario",
        "fondo_garantia": "Inversión SIPC / Lituania",
        "url_afiliado": "https://tu-enlace-de-afiliado-aqui.com"
    }
]

def calcular_metricas_fiscales(ofertas, inflacion_estimada=2.2, irpf_tramo_1=0.19):
    """Calcula el rendimiento neto real tras impuestos e inflación."""
    resultados = []
    for item in ofertas:
        tin = item["tin_anual"]
        tin_neto = tin * (1 - irpf_tramo_1)
        rendimiento_real = tin_neto - inflacion_estimada
        
        # Rendimiento en euros para un capital estándar de 10.000 € a 1 año
        ganancia_bruta_10k = 10000 * (tin / 100)
        ganancia_neta_10k = ganancia_bruta_10k * (1 - irpf_tramo_1)

        resultados.append({
            **item,
            "tin_neto": round(tin_neto, 2),
            "rendimiento_real_neto": round(rendimiento_real, 2),
            "ganancia_neta_10k_anual": round(ganancia_neta_10k, 2),
            "ganancia_neta_10k_mensual": round(ganancia_neta_10k / 12, 2)
        })
    return sorted(resultados, key=lambda x: x["tin_anual"], reverse=True)

def generar_resumen_ia(top_ofertas):
    """Genera un análisis semanal del mercado de liquidez."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "El mercado de liquidez se mantiene estable frente a las decisiones de tipos del BCE."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        resumen_datos = "\n".join([f"- {o['entidad']}: {o['tin_anual']}% TIN ({o['tipo_producto']})" for o in top_ofertas[:3]])
        prompt = f"""
        Actúa como analista financiero independiente.
        Analiza las mejores opciones de remuneración de efectivo hoy en España/Europa:
        {resumen_datos}
        
        Redacta un veredicto técnico en 2 párrafos cortos (máximo 70 palabras en total).
        Explica la diferencia de riesgo entre cuenta bancaria tradicional y fondo monetario. Tono riguroso y objetivo.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Actualización de tipos consolidada para el ciclo actual."

def exportar_dataset():
    zona_horaria = pytz.timezone('Europe/Madrid')
    fecha_actualizacion = datetime.now(zona_horaria).strftime("%Y-%m-%d %H:%M")
    
    ranking = calcular_metricas_fiscales(OFERTAS_BANCARIAS)
    analisis_ia = generar_resumen_ia(ranking)
    
    payload = {
        "ultima_actualizacion": fecha_actualizacion,
        "inflacion_referencia": 2.2,
        "analisis_mercado": analisis_ia,
        "ranking": ranking
    }
    
    os.makedirs("public/data", exist_ok=True)
    with open("public/data/cuentas.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Dataset generado con éxito en public/data/cuentas.json")

if __name__ == "__main__":
    exportar_dataset()
