#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h> 
#include <sys/socket.h>
#include <linux/if.h>

#include <netinet/in.h>  
#include <linux/netlink.h>  
#include <linux/rtnetlink.h>  
#include <arpa/inet.h> 

#define NETLINK_SOCKET_BYTES 1024*8



void 
parseNetlinkAddrMsg(struct nlmsghdr *nlh, int new)  
{  
    struct ifaddrmsg *ifa = (struct ifaddrmsg *) NLMSG_DATA(nlh);  
    struct rtattr *rth = IFA_RTA(ifa);  
    int rtl = IFA_PAYLOAD(nlh);  
  
    while(rtl && RTA_OK(rth, rtl)) {  
        if (rth->rta_type == IFA_LOCAL) {  
        uint32_t ipaddr = htonl(*((uint32_t *)RTA_DATA(rth)));  
        char name[IFNAMSIZ];  
        if_indextoname(ifa->ifa_index, name);  
        printf("%s %s address %d.%d.%d.%d\n",  
               name, (new != 0)?"add":"del",  
               (ipaddr >> 24) & 0xff,  
               (ipaddr >> 16) & 0xff,  
               (ipaddr >> 8) & 0xff,  
               ipaddr & 0xff);  
        }  
        rth = RTA_NEXT(rth, rtl);  
    }  
}

int
main() {
	struct sockaddr_nl snl;  //源 socket 地址，相当于sockaddr_in
	struct msghdr msg;		//socket包装体
	struct iovec iov;		//用于把多个消息通过一次系统调用来发送
	//struct nlmsghdr *nlhdr; //netlink数据包头部
	int len = 0;
	char buffer[NETLINK_SOCKET_BYTES];

	memset(&snl, 0, sizeof(snl));
    snl.nl_family = AF_NETLINK;
    snl.nl_pid    = 0;		// Let the kernel assign the pid to the socket
    snl.nl_groups = RTMGRP_IPV4_IFADDR | RTMGRP_LINK;   //监听ip变化、链路变化
    //snl.nl_groups = RTMGRP_NEIGH;   //监听L3到L2的地址映射的改变(arp表项变化) 
	int _fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (_fd < 0) {
	    printf("Could not open netlink socket\n");
	    close (_fd);
		return -1;
    }
    bind(_fd, (struct sockaddr*)&snl, sizeof(struct sockaddr_nl));
    //nlhdr = (struct nlmsghdr *)malloc(NETLINK_SOCKET_BYTES);
	//iov.iov_base = (void *)nlhdr;
	//iov.iov_len = NETLINK_SOCKET_BYTES;
	msg.msg_name = (void *)&(snl);
	msg.msg_namelen = sizeof(snl);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;

	while(1){
        struct nlmsghdr *nlhdr;
        nlhdr = (struct nlmsghdr *)malloc(NETLINK_SOCKET_BYTES);
        iov.iov_base = (void *)nlhdr;
        iov.iov_len = NETLINK_SOCKET_BYTES;
        len = recvmsg(_fd, &msg, 0);
        printf("len : %d\n", len);
        if (len < 0) {
            if (errno == EINTR)continue;
            break;
        }
		while(NLMSG_OK(nlhdr, len) && (nlhdr->nlmsg_type != NLMSG_DONE)){
            //printf("in while\n");
			if (nlhdr->nlmsg_type == RTM_NEWADDR) {  
                //printf("new addr\n");
                parseNetlinkAddrMsg(nlhdr, 1);  
            }else if(nlhdr->nlmsg_type == RTM_DELADDR){  
                //printf("del addr\n");
                parseNetlinkAddrMsg(nlhdr, 0);
            }else if(nlhdr->nlmsg_type == RTM_NEWLINK){  
                printf("new link\n");
            }
            else if(nlhdr->nlmsg_type == RTM_DELLINK){  
                printf("del link\n");
            }

            nlhdr = NLMSG_NEXT(nlhdr, len);
		}
	}
    close(_fd);
    return 0;
}
