const int row_pin[] = {22, 26, 27, 28};
const int col_pin[] = {18, 19, 20, 21};

const int rows = 4, cols = 4;

const int key[rows][cols] = {
  {1,2,3,4},
  {5,6,7,8},
  {9,11,12,13},
  {14,15,16,17}
  };

void setup(){
  Serial.begin(9600);

  for(int i = 0; i<4; i++)
  {
    pinMode(row_pin[i],OUTPUT); //Configuring row_pins as Output Pins
    digitalWrite(row_pin[i],HIGH);//write HIGH to all row pins

    if(i<cols)
    {
      pinMode(col_pin[i],INPUT_PULLUP);//configure column pin as Input and activate internal //Pullup resistor
    }
  }
}

void loop(){
  int key = read_key();
  if(key !='\n')
  {
    Serial.println(key);
    delay(200);
  }
}

char read_key(){
  for(int row = 0;row < 4;row++)
  {
    digitalWrite(row_pin[0],HIGH);
    digitalWrite(row_pin[1],HIGH);
    digitalWrite(row_pin[2],HIGH);
    digitalWrite(row_pin[3],HIGH);
    digitalWrite(row_pin[row],LOW);

    for(int col = 0;col<4;col++)
    {
      int col_state = digitalRead(col_pin[col]);
      if(col_state == LOW)
      {
        return key[row][col];
      }
    }
  }
  return '\n';
}
