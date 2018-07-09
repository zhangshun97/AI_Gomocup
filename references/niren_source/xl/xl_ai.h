#ifndef XL_AI_H_INCLUDED
#define XL_AI_H_INCLUDED

uint8_t XlSearch(POSFORMAT pos);
void    XlDispose();
void    XlCancel();
int     XlCheckLastMove(POSFORMAT *p_pos);

#endif //XL_AI_H_INCLUDED
