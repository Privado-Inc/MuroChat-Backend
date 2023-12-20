#ARG app_inspector_image
ARG private_gpt_backend_base
ARG BASE_PATH=/home/ubuntu/install


FROM $private_gpt_backend_base as main

ENV POETRY_VIRTUALENVS_PATH=/home/ubuntu/install/poetry-venv

SHELL [ "/bin/bash", "-c" ]

ENV POETRY_HOME=/home/ubuntu/install/poetry
ENV POETRY_VENV=/home/ubuntu/install/poetry-venv

RUN echo private_gpt_backend_base value $private_gpt_backend_base

WORKDIR /home/ubuntu/install/code/private-gpt-backend
COPY . .

RUN rm -rf /home/ubuntu/install/code/private-gpt-backend/.env

RUN export DEBIAN_FRONTEND=noninteractive && apt update && apt install -y libjpeg-dev zlib1g-dev wkhtmltopdf
RUN poetry check
RUN poetry install --no-interaction --no-cache --without dev
RUN poetry run python -m spacy download en_core_web_lg

RUN chmod +x startup.sh
CMD ["/bin/bash", "startup.sh"]
