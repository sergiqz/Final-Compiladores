# Final-Compiladores
Trabajo Final Compiladores
## Descripción
Este proyecto es un compilador que traduce programas escritos en un lenguaje similar a c++ y la invocación de un codigo en Mars.

## Código
int por2(int a){
	int b=a*2;
	return b;
}
int entre2(int a){
	int b=a/2;
	return b;
}
void main()
{
	int a=6;
	if(a>5){
		a=a+5;
	}
    a=a+1;
    print(a);
    print(" ");
   	a=call por2(a);
   	print(a);
   	print(" ");
   	a=call entre2(a);
   	print(a);
   	print(" ");

   	while(a>0){
   		print(a);
   		a=a-1;
   		print(" ");
   	}
}
