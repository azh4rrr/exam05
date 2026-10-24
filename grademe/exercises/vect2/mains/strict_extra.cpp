#include "vect2.hpp"
#include <iostream>

int main()
{
	const vect2 c(3, -4);
	vect2 a(10, 20);
	vect2 b(-1, 5);

	std::cout << "c: " << c << std::endl;
	std::cout << "c[0] c[1]: " << c[0] << " " << c[1] << std::endl;
	std::cout << "c + c: " << c + c << std::endl;
	std::cout << "c - c: " << c - c << std::endl;
	std::cout << "a - b: " << a - b << std::endl;
	std::cout << "b - a: " << b - a << std::endl;
	std::cout << "c * 3: " << c * 3 << std::endl;
	std::cout << "3 * c: " << 3 * c << std::endl;
	std::cout << "c * 0: " << c * 0 << std::endl;
	std::cout << "c * -2: " << c * -2 << std::endl;
	std::cout << "-c: " << -c << std::endl;
	std::cout << "-(-c): " << -(-c) << std::endl;
	std::cout << "a + b * 2: " << a + b * 2 << std::endl;
	std::cout << "(vect2(2, 2) * 2 == vect2(4, 4)): " << (vect2(2, 2) * 2 == vect2(4, 4)) << std::endl;
	std::cout << "(c == c): " << (c == c) << std::endl;
	std::cout << "(c != c): " << (c != c) << std::endl;
	std::cout << "(a == b): " << (a == b) << std::endl;
	std::cout << "(a != b): " << (a != b) << std::endl;
	std::cout << "(vect2(3, 5) == vect2(3, 4)): " << (vect2(3, 5) == vect2(3, 4)) << std::endl;
	std::cout << "(vect2(3, 5) == vect2(2, 5)): " << (vect2(3, 5) == vect2(2, 5)) << std::endl;

	(a += b) += c;
	std::cout << "(a += b) += c: " << a << std::endl;
	(a -= c) -= b;
	std::cout << "(a -= c) -= b: " << a << std::endl;
	(a *= 2) *= -3;
	std::cout << "(a *= 2) *= -3: " << a << std::endl;
	++(++a);
	std::cout << "++(++a): " << a << std::endl;
	--(--a);
	std::cout << "--(--a): " << a << std::endl;
	vect2 old = a++;
	std::cout << "old, a: " << old << " " << a << std::endl;
	old = a--;
	std::cout << "old, a: " << old << " " << a << std::endl;

	vect2 d;
	d[0] = 7;
	d[1] = -8;
	std::cout << "d: " << d << std::endl;
	d[0] += 3;
	d[1]++;
	std::cout << "d: " << d << std::endl;

	vect2 e(d);
	vect2 f;
	f = e;
	e[0] = 0;
	std::cout << "d e f: " << d << " " << e << " " << f << std::endl;
	vect2 &same = f;
	f = same;
	std::cout << "f: " << f << std::endl;
	vect2 g, h;
	g = h = c;
	std::cout << "g h: " << g << " " << h << std::endl;
	std::cout << c << c * 2 << -c << std::endl;
	return 0;
}
