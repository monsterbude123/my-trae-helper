package com.example.app.util;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class GreeterTest {
    @Test
    void greetsValidName() {
        assertEquals("Hello, Alice!", Greeter.greet("Alice"));
    }

    @Test
    void rejectsEmptyName() {
        assertThrows(IllegalArgumentException.class, () -> Greeter.greet(""));
    }

    @Test
    void rejectsNullName() {
        assertThrows(IllegalArgumentException.class, () -> Greeter.greet(null));
    }
}