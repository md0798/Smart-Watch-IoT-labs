package com.example.lab4;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    ImageView speechButton;
    EditText speechText;
    TextView responseShow;
    TextView currentTime;

    private static final int RECOGNIZER_RESULT = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        speechButton = findViewById(R.id.imageView);
        speechText = findViewById(R.id.editTextTextPersonName);
        responseShow = findViewById(R.id.textView4);
        currentTime = findViewById(R.id.currentTime);

        speechButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                Intent speechIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                speechIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                speechIntent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speech to text");
                startActivityForResult(speechIntent,RECOGNIZER_RESULT);
            }
        });
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {

        if(requestCode == RECOGNIZER_RESULT && resultCode == RESULT_OK) {
            ArrayList<String> matches = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            speechText.setText(matches.get(0).toString());

            ApiInterface x = ApiClient.getClient().create(ApiInterface.class);
            SendMessage y =  new SendMessage(matches.get(0).toString());
            Call<ResponseAPI> call3 = x.sendMessage(y);

            call3.enqueue(new Callback<ResponseAPI>() {
                @Override
                public void onResponse(Call<ResponseAPI> call, Response<ResponseAPI> response) {
                    String responseMsg = response.body().responseMessage;
                    Log.v("response", responseMsg);
                    responseShow.setText(responseMsg);
                    //Toast.makeText(getBaseContext(), responseMsg, Toast.LENGTH_LONG).show();

                    if (responseMsg.equalsIgnoreCase("Display Time")) {
                        Calendar c = Calendar.getInstance();

                        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm");
                        String formattedDate = df.format(c.getTime());

                        currentTime.setText(formattedDate);
                        currentTime.setVisibility(View.VISIBLE);
                    } else {
                        currentTime.setVisibility(View.GONE);
                    }

                }

                @Override
                public void onFailure(Call<ResponseAPI> call, Throwable t) {
                    call.cancel();
                }
            });

        }

        super.onActivityResult(requestCode, resultCode, data);
    }
}