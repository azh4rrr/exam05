#pragma once;

#include <iostream>

class vect2{
	private:
		int x ; 
		int y;
	public:
		vect2() : x(0), y(0){}
		vect2(int _x, int _y) : x(_x), y(_y){}
		vect2(const vect2 &oth) {
			x = oth.x;
			y = oth.y;
		}
		vect2 &operator=(const vect2 &oth){
			if(this != &oth){
				x = oth.x;
				y = oth.y;
			}
			return *this;
		}

		int operator[](int i)const{
			if(i == 0)
				return x;
			return y;
		}

		int &operator[](int i)const{
			if(i == 0)
				return x;
			return y;
		}

		vect2 operator+(const vect2 &oth)const{
			return(vect2(x + oth.x, y + oth.y));
		}

		vect2 &operator+=(const vect2 &oth){
			x += oth.x;
			y += oth.y;
			return *this;
		}
		vect2 &operator++(){
			x++;
			y++;
			return *this;
		}
		vect2 &operator++(int){
			vect2 v = *this;
			x++;
			y++;
			return v;
		}

		vect2 operator-(const vect2 &oth)const{
			return(vect2(x - oth.x, y - oth.y));
		}

		vect2 &operator-=(const vect2 &oth){
			x -= oth.x;
			y -= oth.y;
			return *this;
		}
		vect2 &operator--(){
			x--;
			y--;
			return *this;
		}
		vect2 &operator--(int){
			vect2 v = *this;
			x--;
			y--;
			return v;
		}
		vect2 operator-()const{
			return(vect2(-x, -y));
		}

		vect2 operator*(int s)const{
			return(vect2(x * s, y * s));
		}
		vect2 &operator*=(int s){
			x *= s;
			y *= s;
			return this;
		}

		friend vect2 operator*(const vect2 &v, int s){
			return(vect2(v.x * s, v.y * s));
		}

		bool operator==(const vect2 &v)const{
			if(x == v.x && y == v.y)
				return true;
			return false;
		}

		bool operator!=(const vect2 &v)const{
			if(x != v.x || y != v.y)
				return true;
			return false;
		}
		friend std::ostream &operator<<(std::ostream &os, const vect2 &v){
			os << "{" << vect2[0] << ", " << vect2[1] << "}";
			return s;
		}


}