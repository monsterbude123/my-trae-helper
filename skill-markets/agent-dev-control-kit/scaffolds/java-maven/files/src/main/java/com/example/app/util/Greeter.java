package com.example.app.util;

public final class Greeter {
    private Greeter() {}

    public static String greet(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must be non-blank");
        }
        return "Hello, " + name + "!";
    }
}