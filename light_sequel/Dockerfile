FROM golang:1.14.2

WORKDIR /usr/local/go/src/light_sequel
COPY . .
RUN go mod vendor
RUN go build
CMD ["./light_sequel"]