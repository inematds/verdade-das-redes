# Configuração por etapa

Edite tipo/motor/modelo/esforco de `auto/ia.yaml`; exemplos com # no próprio arquivo. `python3 auto/ia_motor.py ver` lista e `configurar ETAPA --tipo assinatura --motor claude --modelo claude-opus-5-5 --esforco medium` altera sem remover comentários. APIs de texto não executam MCP; assinatura Claude/Codex exige o conector da conta correspondente. APIs de modelos desativadas. Credenciais nunca são copiadas.

Metritds usa Codex ~/.codex-2 + metricool-inematds, ownerUsername inematds@gmail.com. Pub2 mantém Claude assinatura + metricool-pub2, ownerUsername inemafuturostds@gmail.com; mudar para Codex exige autenticar essa conta separada, nunca reutilizar OAuth do metritds. Consulta de agenda sem sucesso impede agendamento. Intervalo e registros por marca preservados. Ler a agenda não autoriza publicar.

Coletas analíticas só permitem ferramentas de leitura; resultado deve conter rows e contagem consistente. Publicação mantém portões/horários/canais do sistema chamador. Não há fallback para API paga nem mudança de horários do timer.
