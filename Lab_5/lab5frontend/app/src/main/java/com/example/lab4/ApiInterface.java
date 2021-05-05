package com.example.lab4;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface ApiInterface {

    @POST(".")
    Call<ResponseAPI> sendMessage(@Body SendMessage text);

}


