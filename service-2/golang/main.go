package main

import (
	context2 "context"
	"github.com/dapr/go-sdk/client"
	"github.com/gin-gonic/gin"
	"golang.org/x/net/context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
)

const (
	StateKey = "dapr-series-go"
	StoreName = "statestore-2"
)

var daprClient client.Client

type StateRequest struct {
	Message string `json:"message"`
}

func handleT1() gin.HandlerFunc {
    return func(context *gin.Context) {
        context.JSON(200, gin.H{
            "message": "received",
        })
    }
}

func getState() gin.HandlerFunc {
	return func(context *gin.Context) {
		if data, eTag, err := daprClient.GetState(context2.Background(), StoreName, StateKey); err != nil {
			context.JSON(404, gin.H{
				"message": "Not found",
			})
		} else {
			context.JSON(200, gin.H{
				"state": string(data),
				"eTag": eTag,
			})
		}
	}
}

func saveState() gin.HandlerFunc {
	return func(context *gin.Context) {
		var data StateRequest
		if e := context.Bind(&data); e != nil {
			context.JSON(http.StatusBadRequest, gin.H{"error": e.Error()})
			return
		}
		request := &client.State{
			StoreName: StoreName,
			States: []*client.StateItem{
				{
					Key: StateKey,
					Value: []byte(data.Message),
				},
			},
		}
		if e := daprClient.SaveState(context2.Background(), request); e != nil {
			context.JSON(http.StatusBadRequest, gin.H{"error": e.Error()})
			return
		} else {
			context.JSON(200, gin.H{
				"message": "State Persisted",
			})
		}
	}
}

func ping() gin.HandlerFunc {
	return func(context *gin.Context) {
		context.JSON(200, gin.H{
			"message": "ping",
		})
	}
}

func main() {
	r := gin.New()
	r.Use(gin.Logger())
	r.Use(gin.Recovery())

	r.GET("/ping", ping())
	r.GET("/state", getState())
	r.POST("/state", saveState())
    r.POST("/t1", handleT1())

	s := &http.Server{
		Addr: ":7070",
		Handler: r,
	}

	go func() {
		if err := s.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			panic(err)
		}
	}()

	done := make(chan os.Signal)
	signal.Notify(done, os.Interrupt)
	<-done

	daprClient.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := s.Shutdown(ctx); err != nil {
		log.Fatal("Server Shutdown:", err)
	}
	log.Println("Server exiting")
}

func init()  {
	if c, e := client.NewClient(); e != nil {
		panic(e)
	} else {
		daprClient = c
	}
}