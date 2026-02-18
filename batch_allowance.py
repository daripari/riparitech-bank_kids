# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime
from core.database import run_query

def process_allowances_for_date(processing_date):
    """
    Processo Batch para Pagamento de Mesadas para uma data específica.
    Deve ser chamado por um orquestrador de batches.
    """
    print(f"[{datetime.now()}] Iniciando Batch de Mesadas para a data: {processing_date}...")
    
    try:
        # 1. Busca todas as mesadas configuradas
        allowances = run_query("SELECT * FROM allowances")
        
        if allowances is not None and not allowances.empty:
            # Use a data de processamento fornecida
            today_day = processing_date.day
            today_weekday = processing_date.weekday() # 0=Segunda, 6=Domingo
            
            count = 0
            
            for _, row in allowances.iterrows():
                should_pay = False
                freq = row.get('frequency', 'monthly')
                scheduled_day = int(row['day_of_month'])
                last_paid = pd.to_datetime(row['last_paid']).date() if pd.notnull(row['last_paid']) else None
                
                # Lógica Mensal
                if freq == 'monthly':
                    # Paga APENAS se o dia do processamento for o dia agendado
                    if today_day == scheduled_day:
                        # Verifica se já não foi pago na data de processamento ou depois
                        if not last_paid or last_paid < processing_date:
                            should_pay = True
                            
                # Lógica Semanal
                elif freq == 'weekly':
                    # Paga APENAS se o dia da semana do processamento for o dia agendado
                    if today_weekday == scheduled_day:
                        # Verifica se já não foi pago na data de processamento ou depois
                        if not last_paid or last_paid < processing_date:
                            should_pay = True
                
                if should_pay:
                    desc = f"Mesada Automática ({freq})"
                    print(f" > Pagando R$ {row['amount']} para User ID {row['user_id']} referente a {processing_date}")
                    
                    # Insere Transação
                    run_query("""
                        INSERT INTO transactions (user_id, amount, description, timestamp, type) 
                        VALUES (:u, :a, :d, :ts, 'Mesada')
                    """, {'u': row['user_id'], 'a': row['amount'], 'd': desc, 'ts': processing_date}, commit=True)
                    
                    # Atualiza Data de Pagamento
                    run_query("UPDATE allowances SET last_paid = :now WHERE id=:id", 
                              {'now': processing_date, 'id': row['id']}, commit=True)
                    count += 1
            
            print(f"[{datetime.now()}] Batch para {processing_date} finalizado. {count} pagamentos realizados.")
        else:
            print(f"[{datetime.now()}] Nenhuma mesada configurada para processar em {processing_date}.")
            
    except Exception as e:
        print(f"ERRO CRÍTICO NO BATCH para {processing_date}: {e}")

# O bloco if __name__ == "__main__" foi removido pois a execução agora é controlada pelo app_kids_bank.py
