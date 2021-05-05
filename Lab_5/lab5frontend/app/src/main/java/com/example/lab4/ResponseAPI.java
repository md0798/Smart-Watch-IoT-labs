package com.example.lab4;

import com.google.gson.annotations.SerializedName;

public class ResponseAPI {

    @SerializedName("Device")
    public Device device;
    @SerializedName("ResponseMessage")
    public String responseMessage;

    public ResponseAPI(Device device, String responseMessage) {
        this.device = device;
        this.responseMessage = responseMessage;
    }

}