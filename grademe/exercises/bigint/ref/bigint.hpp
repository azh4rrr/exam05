#ifndef BIGINT_HPP
#define BIGINT_HPP

#include <iostream>
#include <string>
#include <vector>

// Reference solution used by the grader to compute the expected output.
class bigint
{
	private:
		std::vector<int>	digits; // least significant digit first
		void		trim();
		unsigned	to_shift() const;
	public:
		bigint();
		bigint(unsigned long long n);
		bigint(const bigint &other);
		bigint &operator=(const bigint &other);
		~bigint();

		bigint	operator+(const bigint &o) const;
		bigint	&operator+=(const bigint &o);
		bigint	&operator++();
		bigint	operator++(int);

		bigint	operator<<(unsigned n) const;
		bigint	operator>>(unsigned n) const;
		bigint	&operator<<=(unsigned n);
		bigint	&operator>>=(unsigned n);
		bigint	&operator>>=(const bigint &n);
		bigint	&operator<<=(const bigint &n);

		bool	operator==(const bigint &o) const;
		bool	operator!=(const bigint &o) const;
		bool	operator<(const bigint &o) const;
		bool	operator>(const bigint &o) const;
		bool	operator<=(const bigint &o) const;
		bool	operator>=(const bigint &o) const;

		friend std::ostream	&operator<<(std::ostream &os, const bigint &b);
};

#endif
