package com.example.app;

import com.example.app.util.Greeter;

public final class App {
    private App() {}

    public static void main(String[] args) {
        System.out.println(Greeter.greet("World"));
    }
}