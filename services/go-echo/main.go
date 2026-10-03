package main

import (
	"log"
	"net"
	"net/http"
	"os"
	"strconv"
	"sync"

	"github.com/labstack/echo/v5"
)

type HelloResponse struct {
	Message   string `json:"message"`
	Framework string `json:"framework"`
}

func main() {
	workers := 1
	if value, err := strconv.Atoi(os.Getenv("ECHO_WORKERS")); err == nil && value > 0 {
		workers = value
	}

	listener, err := net.Listen("tcp", ":8000")
	if err != nil {
		log.Fatal(err)
	}

	var group sync.WaitGroup
	for worker := 0; worker < workers; worker++ {
		e := echo.New()
		e.GET("/", func(c *echo.Context) error {
			return c.JSON(http.StatusOK, HelloResponse{
				Message:   "hello",
				Framework: "go-echo",
			})
		})

		server := &http.Server{Handler: e}
		group.Add(1)
		go func() {
			defer group.Done()
			if serveErr := server.Serve(listener); serveErr != nil && serveErr != http.ErrServerClosed {
				log.Printf("echo worker stopped: %v", serveErr)
			}
		}()
	}

	log.Printf("Echo started with %d workers", workers)
	group.Wait()
}
