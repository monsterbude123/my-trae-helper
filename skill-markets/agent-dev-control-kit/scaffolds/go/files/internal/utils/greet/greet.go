// Package greet provides a small greeting utility.
package greet

import "fmt"

// Greet returns a greeting for the given name.
//
// It returns an error if name is empty.
func Greet(name string) (string, error) {
	if name == "" {
		return "", fmt.Errorf("name must be non-empty")
	}
	return fmt.Sprintf("Hello, %s!", name), nil
}