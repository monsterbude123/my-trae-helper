//go:build integration

package integration

import (
	"os/exec"
	"testing"
)

func TestBinaryRuns(t *testing.T) {
	cmd := exec.Command("go", "run", "./cmd/app")
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("binary failed: %v\n%s", err, out)
	}
}