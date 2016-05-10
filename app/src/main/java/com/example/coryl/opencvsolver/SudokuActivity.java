package com.example.coryl.opencvsolver;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.GridView;
import android.widget.TextView;

import java.util.Arrays;

public class SudokuActivity extends AppCompatActivity {

    String solution = "";
    GridView gridView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sudoku);

        Intent intent = getIntent();
        solution = intent.getExtras().getString("solution");

        assert solution != null;
        String[] temp = solution.split("");
        String[] solution_array = Arrays.copyOfRange(temp, 1, temp.length);

        gridView = (GridView) findViewById(R.id.gridView1);

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, solution_array);
        gridView.setAdapter(adapter);
    }
}
