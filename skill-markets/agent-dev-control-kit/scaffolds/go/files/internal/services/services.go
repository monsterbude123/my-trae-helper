// Package services exposes the application's top-level operations.
package services

import (
	"fmt"

	"github.com/example/my-go-app/internal/utils/greet"
)

// Run executes the main workflow and returns the first error encountered.
func Run() error {
	fmt.Println(greet.Greet("World"))
	return nil
}