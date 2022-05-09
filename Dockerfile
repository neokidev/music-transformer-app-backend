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
ENV PATH=/project/pkgs/bin:$PATH
ENV PYTHONPATH=/project/pkgs/lib
COPY --from=builder /project/__pypackages__/3.7/bin /project/pkgs/bin
COPY --from=builder /project/__pypackages__/3.7/lib /project/pkgs/lib

# copy files
COPY src/ /project/src
COPY examples/ /project/examples

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
