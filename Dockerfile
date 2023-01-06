# build stage
FROM python:3.7 AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /project/

# install dependencies and project
WORKDIR /project
RUN pdm install --prod --no-lock --no-editable


# run stage
FROM python:3.7

WORKDIR /project
EXPOSE 80

# retrieve packages from build stage
COPY --from=builder /project/.venv /project/.venv
ENV PATH /project/.venv/bin:$PATH
# ENV PATH=/project/pkgs/bin:$PATH
# ENV PYTHONPATH=/project/pkgs/lib
# COPY --from=builder /project/__pypackages__/3.7/bin /project/pkgs/bin
# COPY --from=builder /project/__pypackages__/3.7/lib /project/pkgs/lib

# copy files
COPY src/ /project/src
COPY examples/ /project/examples

RUN apt-get update -y
# RUN apt-get install libsndfile1 -y
RUN apt-get install curl fluidsynth build-essential libsndfile1 libasound2-dev libjack-dev -y
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update -y
RUN apt-get install google-cloud-sdk -y

RUN mkdir content
RUN mkdir checkpoints

RUN gsutil -q -m cp -r gs://magentadata/models/music_transformer/primers/* content
RUN gsutil -q -m cp gs://magentadata/soundfonts/Yamaha-C5-Salamander-JNv5.1.sf2 content
RUN gsutil -q -m cp -r gs://magentadata/models/music_transformer/checkpoints/* checkpoints

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
