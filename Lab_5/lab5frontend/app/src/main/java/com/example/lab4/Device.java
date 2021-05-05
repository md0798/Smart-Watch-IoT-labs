package com.example.lab4;

import com.google.gson.annotations.SerializedName;

public class Device {

    @SerializedName("Feather")
    public String feather;

    @SerializedName("ESP")
    public int esp;

    public Device(String feather, int esp) {
        this.feather = feather;
        this.esp = esp;
    }

}