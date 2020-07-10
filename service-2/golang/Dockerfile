FROM golang:1.14.4-alpine3.12 as base

RUN mkdir /dapr-series
WORKDIR /dapr-series

COPY go.mod .
COPY go.sum .
RUN go mod download

COPY . .

RUN go build -o dapr-series

FROM alpine:3.12.0
RUN apk add --update --no-cache ca-certificates git
COPY --from=base /dapr-series/dapr-series /dapr-series
RUN chmod 755 /dapr-series
ENTRYPOINT ["/dapr-series"]
