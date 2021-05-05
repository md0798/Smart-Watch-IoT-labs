package com.example.lab4;

import com.google.gson.annotations.SerializedName;

public class SendMessage {

    @SerializedName("text")
    public String text;

    public SendMessage(String text) {
        this.text = text;
    }

}
