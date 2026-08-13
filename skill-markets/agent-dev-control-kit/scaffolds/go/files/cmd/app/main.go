package main

import (
	"fmt"
	"os"

	"github.com/example/my-go-app/internal/services"
)

func main() {
	if err := services.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}