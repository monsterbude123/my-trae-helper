package greet

import (
	"testing"
)

func TestGreet(t *testing.T) {
	got, err := Greet("Alice")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != "Hello, Alice!" {
		t.Errorf("got %q, want %q", got, "Hello, Alice!")
	}
}

func TestGreetEmpty(t *testing.T) {
	if _, err := Greet(""); err == nil {
		t.Fatal("expected error for empty name, got nil")
	}
}