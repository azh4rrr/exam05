#pragma once 

#include <iostream>
#include <algorithm>

typedef std::string str;

class bigint
{
	public:
		str num;
		bigint() : num("0"){}
		bigint(unsigned long long nb) : num(std::to_string(nb)){}
		bigint(str nb) : num(nb){}
		bigint(const bigint &bi): num(bi.num){}
		bigint operator-(const bigint &bi) const
		{
			return bigint(0);
		}
		// add string
		str add_str(str a, str b) const
		{
			int i = a.size() - 1;
			int j = b.size() - 1;
			int carry = 0;
			str res = "";
			while(j >= 0 || i >= 0 || carry)
			{
				int sum = carry;
				if (i >= 0) sum += a[i--] - '0';
				if (j >= 0) sum += b[j--] - '0';
				res += (sum % 10) + '0';
				carry = sum / 10;
			}
			std::reverse(res.begin(), res.end());
			return res;
 		}

		bigint operator+(const bigint &bi) const
		{
			return bigint(add_str(num, bi.num));
		}
		bigint operator+=(const bigint &bi)
		{
			num = add_str(num, bi.num);
			return *this;
		}
		bigint operator++()
		{
			*this += bigint(1);
			return *this;
		}
		bigint operator++(int)
		{
			bigint tmp = *this;
			++(*this);
			return tmp;
		}
		bigint operator<<=(int shift)
		{
			if (num == "0")
				return *this;
			for(int i = 0; i < shift; i++)
			{
				num += "0";
			}
			return *this;
		}
		bigint operator<<(int shift) 
		{
			*this <<= shift;
			return *this;
		}
		bigint operator>>=(int shift)
		{
			if (shift >= num.size())
				num = "0";
			else
				num.erase(num.size() - shift);
			return *this;
		}
		bigint operator>>=(const bigint &bi)
		{
			int shift = std::stoi(bi.num);
			return *this >>= shift;
		}
		bool operator<(const bigint &bi) const
		{
			if (num.size() != bi.num.size())
				return num.size() < bi.num.size();
			return num < bi.num;
		}
		bool operator>(const bigint &bi) const
		{
			return (bi < *this);
		}
		bool operator==(const bigint &bi) const
		{
			if (num == bi.num)
				return true;
			return false;
		}
		bool operator!=(const bigint &bi) const
		{
			if (num != bi.num)
				return true;
			return false;
		}

		bool operator<=(const bigint &bi) const
		{
			if (num.size() != bi.num.size())
				return num.size() <= bi.num.size();
			return num <= bi.num;
		}
		bool operator>=(const bigint &bi) const
		{
			return (bi <= *this);
		}


		
		friend std::ostream &operator<<(std::ostream &os, const bigint &bi)
		
		{
			os << bi.num;
			return os;
		}
};