import json
import os
from datetime import date, datetime
from typing import Optional

import openai
from logger import get_logger
from models import Bairro, Demanda, Fonte, TipoDemanda, Usuario, db

logger = get_logger(__name__)


class DemandProcessor:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        logger.info("DemandProcessor initialized", model=self.model)

    async def process_message(
        self, message_text: str, user_id: int, user_name: str
    ) -> Optional[dict]:
        """
        Processa uma mensagem do Telegram usando OpenAI e salva no banco
        """
        try:
            # Gerar ID único para rastreamento
            raw_text_id = f"tg_{user_id}_{int(datetime.now().timestamp())}"

            logger.info("Processing message", raw_text_id=raw_text_id, user_id=user_id)

            # 1. Processar com OpenAI
            extracted_data = await self._extract_demand_data(message_text)

            if not extracted_data:
                logger.warning("No demand data extracted", raw_text_id=raw_text_id)
                return None

            # 2. Salvar no banco
            demanda_id = await self._save_to_database(
                raw_text_id=raw_text_id,
                message_text=message_text,
                user_id=user_id,
                user_name=user_name,
                extracted_data=extracted_data,
            )

            logger.info(
                "Demand processed successfully",
                raw_text_id=raw_text_id,
                demanda_id=demanda_id,
            )

            return {
                "demanda_id": demanda_id,
                "raw_text_id": raw_text_id,
                "extracted_data": extracted_data,
            }

        except Exception as e:
            logger.error(
                "Error processing message",
                raw_text_id=raw_text_id if "raw_text_id" in locals() else None,
                error=str(e),
                exc_info=True,
            )
            return None

    async def _extract_demand_data(self, message_text: str) -> Optional[dict]:
        """
        Extrai dados estruturados da mensagem usando OpenAI
        """
        try:
            prompt = f"""
Você está analisando um RELATO DE AGENTE PÚBLICO que conversou com um cidadão sobre uma demanda de serviço público.

MENSAGEM DO AGENTE: "{message_text}"

O padrão típico é: "[data] falei com [NOME DO CIDADÃO] [onde conversaram], [PROBLEMA] [onde é o problema], telefone [telefone], [observações]"

Extraia as informações estruturadas e retorne um JSON:

{{
    "eh_demanda": true/false,
    "nome_cidadao": "nome do cidadão que relatou o problema",
    "telefone": "telefone do cidadão",
    "bairro": "bairro onde ESTÁ o problema",
    "local_especifico": "rua/endereço específico onde está o problema",
    "tipo_servico": "que serviço público é necessário",
    "descricao_problema": "descrição clara do problema",
    "urgencia": 1-5 (baseado nas observações),
    "observacoes": "observações sobre urgência/contexto"
}}

EXEMPLOS DE EXTRAÇÃO:

Entrada: "Hoje 18/07 falei com Maria Silva na Praça Central, bueiro entupido na esquina da Rua A com Rua B, telefone 11 99999-8888, urgente porque tem crianças passando"
{{
    "eh_demanda": true,
    "nome_cidadao": "Maria Silva",
    "telefone": "11 99999-8888",
    "bairro": "Praça Central",
    "local_especifico": "esquina da Rua A com Rua B",
    "tipo_servico": "Limpeza de bueiro",
    "descricao_problema": "Bueiro entupido",
    "urgencia": 4,
    "observacoes": "Urgente porque tem crianças passando"
}}

TIPOS DE SERVIÇO (escolha o mais adequado):
- "Limpeza de bueiro"
- "Reparo de iluminação"
- "Poda de árvore"
- "Tratamento de árvore"
- "Tapa-buraco"
- "Reparo de fiação"
- "Limpeza de via"
- "Desobstrução de drenagem"

URGÊNCIA:
- 1: não urgente, estético
- 2: pouco urgente, trânsito normal
- 3: moderado
- 4: urgente (crianças, cheiro, etc.)
- 5: crítico (risco iminente, afogamento, choque)

IMPORTANTE:
- Se a mensagem não descreve um problema público, marque "eh_demanda": false
- Use null apenas para informações realmente ausentes
- O "bairro" é onde está o PROBLEMA, não onde foi a conversa
- Seja específico no "tipo_servico" baseado no problema descrito
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )

            result_text = response.choices[0].message.content.strip()

            # Tentar extrair JSON da resposta
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()

            extracted_data = json.loads(result_text)

            # Validar se é uma demanda válida
            if not extracted_data.get("eh_demanda", False):
                logger.info("Message is not a demand", message=message_text[:100])
                return None

            logger.info(
                "Data extracted successfully", confianca=extracted_data.get("confianca")
            )
            return extracted_data

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse OpenAI JSON response",
                response=result_text,
                error=str(e),
            )
            return None
        except Exception as e:
            logger.error("Error in OpenAI extraction", error=str(e), exc_info=True)
            return None

    async def _save_to_database(
        self,
        raw_text_id: str,
        message_text: str,
        user_id: int,
        user_name: str,
        extracted_data: dict,
    ) -> Optional[int]:
        """
        Salva os dados processados no banco de dados
        """
        try:
            # Buscar ou criar entidades relacionadas
            bairro_id = await self._get_or_create_bairro(extracted_data.get("bairro"))

            # Usar tipo_servico extraído pela LLM
            tipo_especifico = extracted_data.get("tipo_servico")
            logger.info(
                "DEBUG - Tipo de serviço extraído pela OpenAI",
                tipo_especifico=tipo_especifico,
            )

            if not tipo_especifico:
                # Fallback para "Outros" se não extraiu nenhum tipo
                tipo_especifico = "Outros"
                logger.info(
                    "DEBUG - Usando fallback 'Outros'", tipo_especifico=tipo_especifico
                )
            else:
                logger.info(
                    "DEBUG - Usando tipo de serviço específico",
                    tipo_especifico=tipo_especifico,
                )

            tipo_demanda_id = await self._get_or_create_tipo_demanda(tipo_especifico)
            logger.info(
                "DEBUG - Tipo demanda ID criado",
                tipo_demanda_id=tipo_demanda_id,
                tipo_especifico=tipo_especifico,
            )

            fonte_id = await self._get_or_create_fonte("Telegram")
            agente_id = await self._get_or_create_usuario("Bot OpenAI", "bot")

            # Processar dados de contato
            data_contato = date.today()
            hora_contato = datetime.now().time()

            # Criar demanda
            demanda = Demanda(
                raw_text_id=raw_text_id,
                data_contato=data_contato,
                hora_contato=hora_contato,
                nome=extracted_data.get("nome_cidadao") or user_name,
                telefone=extracted_data.get("telefone"),
                bairro_id=bairro_id,
                referencia_local=extracted_data.get("local_especifico"),
                tipo_demanda_id=tipo_demanda_id,
                descricao_curta=extracted_data.get("descricao_problema"),
                prioridade_percebida="alta"
                if extracted_data.get("urgencia", 1) >= 4
                else "media",
                urgencia=extracted_data.get("urgencia", 1),
                impacto=extracted_data.get(
                    "urgencia", 1
                ),  # Usando urgência como impacto por simplicidade
                status="nova",
                consentimento_comunicacao=True,
                fonte_id=fonte_id,
                canal_origem="telegram",
                confianca_global=0.9,  # Alta confiança para relatos de agentes
                flags={"telegram_user_id": user_id, "relato_agente": True},
                metadata_json={
                    "openai_extraction": extracted_data,
                    "original_message_length": len(message_text),
                },
                revisado=False,
                agente_id=agente_id,
                texto_original=message_text,
                timestamp_processamento=datetime.now(),
                timestamp_captura=datetime.now(),
            )

            db.session.add(demanda)
            db.session.commit()

            logger.info("Demand saved to database", demanda_id=demanda.id_registro)
            return demanda.id_registro

        except Exception as e:
            logger.error("Error saving to database", error=str(e), exc_info=True)
            db.session.rollback()
            return None

    async def _get_or_create_bairro(self, nome_bairro: Optional[str]) -> Optional[int]:
        """Busca ou cria um bairro"""
        if not nome_bairro:
            return None

        bairro = Bairro.query.filter_by(nome=nome_bairro.title()).first()
        if not bairro:
            bairro = Bairro(nome=nome_bairro.title(), ativo=True)
            db.session.add(bairro)
            db.session.flush()

        return bairro.id

    async def _get_or_create_tipo_demanda(self, tipo: Optional[str]) -> Optional[int]:
        """Busca ou cria um tipo de demanda usando classificação livre da LLM"""
        if not tipo:
            tipo = "Outros"

        # Usar o tipo específico exatamente como a LLM retornou
        nome_tipo = tipo.strip().title()
        logger.info(
            "DEBUG - Criando tipo demanda livre", input_tipo=tipo, nome_tipo=nome_tipo
        )

        tipo_demanda = TipoDemanda.query.filter_by(nome=nome_tipo).first()
        if not tipo_demanda:
            logger.info("DEBUG - Novo tipo de serviço, criando", nome_tipo=nome_tipo)

            tipo_demanda = TipoDemanda(
                nome=nome_tipo,
                categoria="Serviços Públicos",  # Categoria genérica
                ativo=True,
            )
            db.session.add(tipo_demanda)
            db.session.flush()
        else:
            logger.info(
                "DEBUG - Tipo de serviço já existe",
                nome_tipo=nome_tipo,
                id=tipo_demanda.id,
            )

        return tipo_demanda.id

    def _get_categoria_from_tipo(self, tipo: str) -> str:
        """Determina a categoria geral baseada no tipo específico"""
        tipo_lower = tipo.lower()

        zeladoria_tipos = [
            "bueiro",
            "buraco",
            "iluminação",
            "lixo",
            "poda",
            "limpeza",
            "calçada",
            "sinalização",
        ]
        saude_tipos = ["posto", "médico", "medicamento", "dengue", "aedes"]
        educacao_tipos = ["escola", "professor", "merenda", "infraestrutura escolar"]
        transporte_tipos = ["ônibus", "ponto", "semáforo"]
        seguranca_tipos = ["policiamento", "drogas", "crime", "insegura"]

        for palavra in zeladoria_tipos:
            if palavra in tipo_lower:
                return "Zeladoria"

        for palavra in saude_tipos:
            if palavra in tipo_lower:
                return "Saúde"

        for palavra in educacao_tipos:
            if palavra in tipo_lower:
                return "Educação"

        for palavra in transporte_tipos:
            if palavra in tipo_lower:
                return "Transporte"

        for palavra in seguranca_tipos:
            if palavra in tipo_lower:
                return "Segurança"

        return "Geral"

    def _inferir_tipo_especifico(self, descricao: str, categoria_geral: str) -> str:
        """Infere o tipo específico baseado na descrição quando LLM retorna categoria geral"""
        descricao_lower = descricao.lower()

        # Mapeamento de palavras-chave para tipos específicos
        zeladoria_tipos = {
            "lâmpada": "Iluminação pública",
            "lampada": "Iluminação pública",
            "poste": "Iluminação pública",
            "luz": "Iluminação pública",
            "iluminação": "Iluminação pública",
            "iluminacao": "Iluminação pública",
            "bueiro": "Bueiro entupido",
            "esgoto": "Bueiro entupido",
            "entupido": "Bueiro entupido",
            "buraco": "Buraco na rua",
            "asfalto": "Buraco na rua",
            "lixo": "Coleta de lixo",
            "coleta": "Coleta de lixo",
            "árvore": "Poda de árvore",
            "arvore": "Poda de árvore",
            "galho": "Poda de árvore",
            "poda": "Poda de árvore",
            "calçada": "Calçada danificada",
            "calcada": "Calçada danificada",
            "sinalização": "Sinalização",
            "sinalizacao": "Sinalização",
            "placa": "Sinalização",
            "semáforo": "Sinalização",
            "semaforo": "Sinalização",
        }

        saude_tipos = {
            "posto": "Posto de saúde",
            "médico": "Falta de médico",
            "medico": "Falta de médico",
            "medicamento": "Medicamento em falta",
            "dengue": "Dengue/Aedes",
            "aedes": "Dengue/Aedes",
            "mosquito": "Dengue/Aedes",
        }

        educacao_tipos = {
            "escola": "Infraestrutura escolar",
            "professor": "Escola sem professor",
            "merenda": "Merenda escolar",
        }

        transporte_tipos = {
            "ônibus": "Ônibus atrasado",
            "onibus": "Ônibus atrasado",
            "ponto": "Ponto de ônibus",
        }

        seguranca_tipos = {
            "policia": "Falta de policiamento",
            "polícia": "Falta de policiamento",
            "segurança": "Falta de policiamento",
            "seguranca": "Falta de policiamento",
            "droga": "Drogas/Crime",
            "crime": "Drogas/Crime",
        }

        # Escolher o mapeamento baseado na categoria
        if categoria_geral == "zeladoria":
            tipos_map = zeladoria_tipos
        elif categoria_geral == "saude":
            tipos_map = saude_tipos
        elif categoria_geral == "educacao":
            tipos_map = educacao_tipos
        elif categoria_geral == "transporte":
            tipos_map = transporte_tipos
        elif categoria_geral == "seguranca":
            tipos_map = seguranca_tipos
        else:
            return "Outros"

        # Procurar palavras-chave na descrição
        for palavra_chave, tipo_especifico in tipos_map.items():
            if palavra_chave in descricao_lower:
                return tipo_especifico

        # Se não encontrou palavra-chave específica, usar categoria geral
        categoria_map = {
            "zeladoria": "Zeladoria Urbana",
            "saude": "Saúde",
            "educacao": "Educação",
            "transporte": "Transporte",
            "seguranca": "Segurança",
        }

        return categoria_map.get(categoria_geral, "Outros")

    async def _get_or_create_fonte(self, nome_fonte: str) -> int:
        """Busca ou cria uma fonte"""
        fonte = Fonte.query.filter_by(nome=nome_fonte).first()
        if not fonte:
            fonte = Fonte(
                nome=nome_fonte,
                descricao=f"Mensagens recebidas via {nome_fonte}",
                ativo=True,
            )
            db.session.add(fonte)
            db.session.flush()

        return fonte.id

    async def _get_or_create_usuario(self, nome: str, tipo: str) -> int:
        """Busca ou cria um usuário"""
        usuario = Usuario.query.filter_by(nome=nome, tipo=tipo).first()
        if not usuario:
            usuario = Usuario(nome=nome, tipo=tipo, ativo=True)
            db.session.add(usuario)
            db.session.flush()

        return usuario.id
