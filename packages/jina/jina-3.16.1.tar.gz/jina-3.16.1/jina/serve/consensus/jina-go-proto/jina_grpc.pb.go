// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v3.13.0
// source: jina.proto

package jina_go_proto

import (
	context "context"
	empty "github.com/golang/protobuf/ptypes/empty"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// JinaDataRequestRPCClient is the client API for JinaDataRequestRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaDataRequestRPCClient interface {
	// Used for passing DataRequests to the Executors
	ProcessData(ctx context.Context, in *DataRequestListProto, opts ...grpc.CallOption) (*DataRequestProto, error)
}

type jinaDataRequestRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaDataRequestRPCClient(cc grpc.ClientConnInterface) JinaDataRequestRPCClient {
	return &jinaDataRequestRPCClient{cc}
}

func (c *jinaDataRequestRPCClient) ProcessData(ctx context.Context, in *DataRequestListProto, opts ...grpc.CallOption) (*DataRequestProto, error) {
	out := new(DataRequestProto)
	err := c.cc.Invoke(ctx, "/jina.JinaDataRequestRPC/process_data", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaDataRequestRPCServer is the server API for JinaDataRequestRPC service.
// All implementations must embed UnimplementedJinaDataRequestRPCServer
// for forward compatibility
type JinaDataRequestRPCServer interface {
	// Used for passing DataRequests to the Executors
	ProcessData(context.Context, *DataRequestListProto) (*DataRequestProto, error)
	mustEmbedUnimplementedJinaDataRequestRPCServer()
}

// UnimplementedJinaDataRequestRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaDataRequestRPCServer struct {
}

func (UnimplementedJinaDataRequestRPCServer) ProcessData(context.Context, *DataRequestListProto) (*DataRequestProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method ProcessData not implemented")
}
func (UnimplementedJinaDataRequestRPCServer) mustEmbedUnimplementedJinaDataRequestRPCServer() {}

// UnsafeJinaDataRequestRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaDataRequestRPCServer will
// result in compilation errors.
type UnsafeJinaDataRequestRPCServer interface {
	mustEmbedUnimplementedJinaDataRequestRPCServer()
}

func RegisterJinaDataRequestRPCServer(s grpc.ServiceRegistrar, srv JinaDataRequestRPCServer) {
	s.RegisterService(&JinaDataRequestRPC_ServiceDesc, srv)
}

func _JinaDataRequestRPC_ProcessData_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DataRequestListProto)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaDataRequestRPCServer).ProcessData(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaDataRequestRPC/process_data",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaDataRequestRPCServer).ProcessData(ctx, req.(*DataRequestListProto))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaDataRequestRPC_ServiceDesc is the grpc.ServiceDesc for JinaDataRequestRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaDataRequestRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaDataRequestRPC",
	HandlerType: (*JinaDataRequestRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "process_data",
			Handler:    _JinaDataRequestRPC_ProcessData_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaSingleDataRequestRPCClient is the client API for JinaSingleDataRequestRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaSingleDataRequestRPCClient interface {
	// Used for passing DataRequests to the Executors
	ProcessSingleData(ctx context.Context, in *DataRequestProto, opts ...grpc.CallOption) (*DataRequestProto, error)
}

type jinaSingleDataRequestRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaSingleDataRequestRPCClient(cc grpc.ClientConnInterface) JinaSingleDataRequestRPCClient {
	return &jinaSingleDataRequestRPCClient{cc}
}

func (c *jinaSingleDataRequestRPCClient) ProcessSingleData(ctx context.Context, in *DataRequestProto, opts ...grpc.CallOption) (*DataRequestProto, error) {
	out := new(DataRequestProto)
	err := c.cc.Invoke(ctx, "/jina.JinaSingleDataRequestRPC/process_single_data", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaSingleDataRequestRPCServer is the server API for JinaSingleDataRequestRPC service.
// All implementations must embed UnimplementedJinaSingleDataRequestRPCServer
// for forward compatibility
type JinaSingleDataRequestRPCServer interface {
	// Used for passing DataRequests to the Executors
	ProcessSingleData(context.Context, *DataRequestProto) (*DataRequestProto, error)
	mustEmbedUnimplementedJinaSingleDataRequestRPCServer()
}

// UnimplementedJinaSingleDataRequestRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaSingleDataRequestRPCServer struct {
}

func (UnimplementedJinaSingleDataRequestRPCServer) ProcessSingleData(context.Context, *DataRequestProto) (*DataRequestProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method ProcessSingleData not implemented")
}
func (UnimplementedJinaSingleDataRequestRPCServer) mustEmbedUnimplementedJinaSingleDataRequestRPCServer() {
}

// UnsafeJinaSingleDataRequestRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaSingleDataRequestRPCServer will
// result in compilation errors.
type UnsafeJinaSingleDataRequestRPCServer interface {
	mustEmbedUnimplementedJinaSingleDataRequestRPCServer()
}

func RegisterJinaSingleDataRequestRPCServer(s grpc.ServiceRegistrar, srv JinaSingleDataRequestRPCServer) {
	s.RegisterService(&JinaSingleDataRequestRPC_ServiceDesc, srv)
}

func _JinaSingleDataRequestRPC_ProcessSingleData_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DataRequestProto)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaSingleDataRequestRPCServer).ProcessSingleData(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaSingleDataRequestRPC/process_single_data",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaSingleDataRequestRPCServer).ProcessSingleData(ctx, req.(*DataRequestProto))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaSingleDataRequestRPC_ServiceDesc is the grpc.ServiceDesc for JinaSingleDataRequestRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaSingleDataRequestRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaSingleDataRequestRPC",
	HandlerType: (*JinaSingleDataRequestRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "process_single_data",
			Handler:    _JinaSingleDataRequestRPC_ProcessSingleData_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaRPCClient is the client API for JinaRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaRPCClient interface {
	// Pass in a Request and a filled Request with matches will be returned.
	Call(ctx context.Context, opts ...grpc.CallOption) (JinaRPC_CallClient, error)
}

type jinaRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaRPCClient(cc grpc.ClientConnInterface) JinaRPCClient {
	return &jinaRPCClient{cc}
}

func (c *jinaRPCClient) Call(ctx context.Context, opts ...grpc.CallOption) (JinaRPC_CallClient, error) {
	stream, err := c.cc.NewStream(ctx, &JinaRPC_ServiceDesc.Streams[0], "/jina.JinaRPC/Call", opts...)
	if err != nil {
		return nil, err
	}
	x := &jinaRPCCallClient{stream}
	return x, nil
}

type JinaRPC_CallClient interface {
	Send(*DataRequestProto) error
	Recv() (*DataRequestProto, error)
	grpc.ClientStream
}

type jinaRPCCallClient struct {
	grpc.ClientStream
}

func (x *jinaRPCCallClient) Send(m *DataRequestProto) error {
	return x.ClientStream.SendMsg(m)
}

func (x *jinaRPCCallClient) Recv() (*DataRequestProto, error) {
	m := new(DataRequestProto)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

// JinaRPCServer is the server API for JinaRPC service.
// All implementations must embed UnimplementedJinaRPCServer
// for forward compatibility
type JinaRPCServer interface {
	// Pass in a Request and a filled Request with matches will be returned.
	Call(JinaRPC_CallServer) error
	mustEmbedUnimplementedJinaRPCServer()
}

// UnimplementedJinaRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaRPCServer struct {
}

func (UnimplementedJinaRPCServer) Call(JinaRPC_CallServer) error {
	return status.Errorf(codes.Unimplemented, "method Call not implemented")
}
func (UnimplementedJinaRPCServer) mustEmbedUnimplementedJinaRPCServer() {}

// UnsafeJinaRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaRPCServer will
// result in compilation errors.
type UnsafeJinaRPCServer interface {
	mustEmbedUnimplementedJinaRPCServer()
}

func RegisterJinaRPCServer(s grpc.ServiceRegistrar, srv JinaRPCServer) {
	s.RegisterService(&JinaRPC_ServiceDesc, srv)
}

func _JinaRPC_Call_Handler(srv interface{}, stream grpc.ServerStream) error {
	return srv.(JinaRPCServer).Call(&jinaRPCCallServer{stream})
}

type JinaRPC_CallServer interface {
	Send(*DataRequestProto) error
	Recv() (*DataRequestProto, error)
	grpc.ServerStream
}

type jinaRPCCallServer struct {
	grpc.ServerStream
}

func (x *jinaRPCCallServer) Send(m *DataRequestProto) error {
	return x.ServerStream.SendMsg(m)
}

func (x *jinaRPCCallServer) Recv() (*DataRequestProto, error) {
	m := new(DataRequestProto)
	if err := x.ServerStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

// JinaRPC_ServiceDesc is the grpc.ServiceDesc for JinaRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaRPC",
	HandlerType: (*JinaRPCServer)(nil),
	Methods:     []grpc.MethodDesc{},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "Call",
			Handler:       _JinaRPC_Call_Handler,
			ServerStreams: true,
			ClientStreams: true,
		},
	},
	Metadata: "jina.proto",
}

// JinaDiscoverEndpointsRPCClient is the client API for JinaDiscoverEndpointsRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaDiscoverEndpointsRPCClient interface {
	EndpointDiscovery(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*EndpointsProto, error)
}

type jinaDiscoverEndpointsRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaDiscoverEndpointsRPCClient(cc grpc.ClientConnInterface) JinaDiscoverEndpointsRPCClient {
	return &jinaDiscoverEndpointsRPCClient{cc}
}

func (c *jinaDiscoverEndpointsRPCClient) EndpointDiscovery(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*EndpointsProto, error) {
	out := new(EndpointsProto)
	err := c.cc.Invoke(ctx, "/jina.JinaDiscoverEndpointsRPC/endpoint_discovery", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaDiscoverEndpointsRPCServer is the server API for JinaDiscoverEndpointsRPC service.
// All implementations must embed UnimplementedJinaDiscoverEndpointsRPCServer
// for forward compatibility
type JinaDiscoverEndpointsRPCServer interface {
	EndpointDiscovery(context.Context, *empty.Empty) (*EndpointsProto, error)
	mustEmbedUnimplementedJinaDiscoverEndpointsRPCServer()
}

// UnimplementedJinaDiscoverEndpointsRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaDiscoverEndpointsRPCServer struct {
}

func (UnimplementedJinaDiscoverEndpointsRPCServer) EndpointDiscovery(context.Context, *empty.Empty) (*EndpointsProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method EndpointDiscovery not implemented")
}
func (UnimplementedJinaDiscoverEndpointsRPCServer) mustEmbedUnimplementedJinaDiscoverEndpointsRPCServer() {
}

// UnsafeJinaDiscoverEndpointsRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaDiscoverEndpointsRPCServer will
// result in compilation errors.
type UnsafeJinaDiscoverEndpointsRPCServer interface {
	mustEmbedUnimplementedJinaDiscoverEndpointsRPCServer()
}

func RegisterJinaDiscoverEndpointsRPCServer(s grpc.ServiceRegistrar, srv JinaDiscoverEndpointsRPCServer) {
	s.RegisterService(&JinaDiscoverEndpointsRPC_ServiceDesc, srv)
}

func _JinaDiscoverEndpointsRPC_EndpointDiscovery_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(empty.Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaDiscoverEndpointsRPCServer).EndpointDiscovery(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaDiscoverEndpointsRPC/endpoint_discovery",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaDiscoverEndpointsRPCServer).EndpointDiscovery(ctx, req.(*empty.Empty))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaDiscoverEndpointsRPC_ServiceDesc is the grpc.ServiceDesc for JinaDiscoverEndpointsRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaDiscoverEndpointsRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaDiscoverEndpointsRPC",
	HandlerType: (*JinaDiscoverEndpointsRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "endpoint_discovery",
			Handler:    _JinaDiscoverEndpointsRPC_EndpointDiscovery_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaGatewayDryRunRPCClient is the client API for JinaGatewayDryRunRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaGatewayDryRunRPCClient interface {
	DryRun(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*StatusProto, error)
}

type jinaGatewayDryRunRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaGatewayDryRunRPCClient(cc grpc.ClientConnInterface) JinaGatewayDryRunRPCClient {
	return &jinaGatewayDryRunRPCClient{cc}
}

func (c *jinaGatewayDryRunRPCClient) DryRun(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*StatusProto, error) {
	out := new(StatusProto)
	err := c.cc.Invoke(ctx, "/jina.JinaGatewayDryRunRPC/dry_run", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaGatewayDryRunRPCServer is the server API for JinaGatewayDryRunRPC service.
// All implementations must embed UnimplementedJinaGatewayDryRunRPCServer
// for forward compatibility
type JinaGatewayDryRunRPCServer interface {
	DryRun(context.Context, *empty.Empty) (*StatusProto, error)
	mustEmbedUnimplementedJinaGatewayDryRunRPCServer()
}

// UnimplementedJinaGatewayDryRunRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaGatewayDryRunRPCServer struct {
}

func (UnimplementedJinaGatewayDryRunRPCServer) DryRun(context.Context, *empty.Empty) (*StatusProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DryRun not implemented")
}
func (UnimplementedJinaGatewayDryRunRPCServer) mustEmbedUnimplementedJinaGatewayDryRunRPCServer() {}

// UnsafeJinaGatewayDryRunRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaGatewayDryRunRPCServer will
// result in compilation errors.
type UnsafeJinaGatewayDryRunRPCServer interface {
	mustEmbedUnimplementedJinaGatewayDryRunRPCServer()
}

func RegisterJinaGatewayDryRunRPCServer(s grpc.ServiceRegistrar, srv JinaGatewayDryRunRPCServer) {
	s.RegisterService(&JinaGatewayDryRunRPC_ServiceDesc, srv)
}

func _JinaGatewayDryRunRPC_DryRun_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(empty.Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaGatewayDryRunRPCServer).DryRun(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaGatewayDryRunRPC/dry_run",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaGatewayDryRunRPCServer).DryRun(ctx, req.(*empty.Empty))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaGatewayDryRunRPC_ServiceDesc is the grpc.ServiceDesc for JinaGatewayDryRunRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaGatewayDryRunRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaGatewayDryRunRPC",
	HandlerType: (*JinaGatewayDryRunRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "dry_run",
			Handler:    _JinaGatewayDryRunRPC_DryRun_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaInfoRPCClient is the client API for JinaInfoRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaInfoRPCClient interface {
	XStatus(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*JinaInfoProto, error)
}

type jinaInfoRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaInfoRPCClient(cc grpc.ClientConnInterface) JinaInfoRPCClient {
	return &jinaInfoRPCClient{cc}
}

func (c *jinaInfoRPCClient) XStatus(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*JinaInfoProto, error) {
	out := new(JinaInfoProto)
	err := c.cc.Invoke(ctx, "/jina.JinaInfoRPC/_status", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaInfoRPCServer is the server API for JinaInfoRPC service.
// All implementations must embed UnimplementedJinaInfoRPCServer
// for forward compatibility
type JinaInfoRPCServer interface {
	XStatus(context.Context, *empty.Empty) (*JinaInfoProto, error)
	mustEmbedUnimplementedJinaInfoRPCServer()
}

// UnimplementedJinaInfoRPCServer must be embedded to have forward compatible implementations.
type UnimplementedJinaInfoRPCServer struct {
}

func (UnimplementedJinaInfoRPCServer) XStatus(context.Context, *empty.Empty) (*JinaInfoProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method XStatus not implemented")
}
func (UnimplementedJinaInfoRPCServer) mustEmbedUnimplementedJinaInfoRPCServer() {}

// UnsafeJinaInfoRPCServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaInfoRPCServer will
// result in compilation errors.
type UnsafeJinaInfoRPCServer interface {
	mustEmbedUnimplementedJinaInfoRPCServer()
}

func RegisterJinaInfoRPCServer(s grpc.ServiceRegistrar, srv JinaInfoRPCServer) {
	s.RegisterService(&JinaInfoRPC_ServiceDesc, srv)
}

func _JinaInfoRPC_XStatus_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(empty.Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaInfoRPCServer).XStatus(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaInfoRPC/_status",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaInfoRPCServer).XStatus(ctx, req.(*empty.Empty))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaInfoRPC_ServiceDesc is the grpc.ServiceDesc for JinaInfoRPC service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaInfoRPC_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaInfoRPC",
	HandlerType: (*JinaInfoRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "_status",
			Handler:    _JinaInfoRPC_XStatus_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaExecutorSnapshotClient is the client API for JinaExecutorSnapshot service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaExecutorSnapshotClient interface {
	Snapshot(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*SnapshotStatusProto, error)
}

type jinaExecutorSnapshotClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaExecutorSnapshotClient(cc grpc.ClientConnInterface) JinaExecutorSnapshotClient {
	return &jinaExecutorSnapshotClient{cc}
}

func (c *jinaExecutorSnapshotClient) Snapshot(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*SnapshotStatusProto, error) {
	out := new(SnapshotStatusProto)
	err := c.cc.Invoke(ctx, "/jina.JinaExecutorSnapshot/snapshot", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaExecutorSnapshotServer is the server API for JinaExecutorSnapshot service.
// All implementations must embed UnimplementedJinaExecutorSnapshotServer
// for forward compatibility
type JinaExecutorSnapshotServer interface {
	Snapshot(context.Context, *empty.Empty) (*SnapshotStatusProto, error)
	mustEmbedUnimplementedJinaExecutorSnapshotServer()
}

// UnimplementedJinaExecutorSnapshotServer must be embedded to have forward compatible implementations.
type UnimplementedJinaExecutorSnapshotServer struct {
}

func (UnimplementedJinaExecutorSnapshotServer) Snapshot(context.Context, *empty.Empty) (*SnapshotStatusProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Snapshot not implemented")
}
func (UnimplementedJinaExecutorSnapshotServer) mustEmbedUnimplementedJinaExecutorSnapshotServer() {}

// UnsafeJinaExecutorSnapshotServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaExecutorSnapshotServer will
// result in compilation errors.
type UnsafeJinaExecutorSnapshotServer interface {
	mustEmbedUnimplementedJinaExecutorSnapshotServer()
}

func RegisterJinaExecutorSnapshotServer(s grpc.ServiceRegistrar, srv JinaExecutorSnapshotServer) {
	s.RegisterService(&JinaExecutorSnapshot_ServiceDesc, srv)
}

func _JinaExecutorSnapshot_Snapshot_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(empty.Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaExecutorSnapshotServer).Snapshot(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaExecutorSnapshot/snapshot",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaExecutorSnapshotServer).Snapshot(ctx, req.(*empty.Empty))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaExecutorSnapshot_ServiceDesc is the grpc.ServiceDesc for JinaExecutorSnapshot service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaExecutorSnapshot_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaExecutorSnapshot",
	HandlerType: (*JinaExecutorSnapshotServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "snapshot",
			Handler:    _JinaExecutorSnapshot_Snapshot_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaExecutorSnapshotProgressClient is the client API for JinaExecutorSnapshotProgress service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaExecutorSnapshotProgressClient interface {
	SnapshotStatus(ctx context.Context, in *SnapshotId, opts ...grpc.CallOption) (*SnapshotStatusProto, error)
}

type jinaExecutorSnapshotProgressClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaExecutorSnapshotProgressClient(cc grpc.ClientConnInterface) JinaExecutorSnapshotProgressClient {
	return &jinaExecutorSnapshotProgressClient{cc}
}

func (c *jinaExecutorSnapshotProgressClient) SnapshotStatus(ctx context.Context, in *SnapshotId, opts ...grpc.CallOption) (*SnapshotStatusProto, error) {
	out := new(SnapshotStatusProto)
	err := c.cc.Invoke(ctx, "/jina.JinaExecutorSnapshotProgress/snapshot_status", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaExecutorSnapshotProgressServer is the server API for JinaExecutorSnapshotProgress service.
// All implementations must embed UnimplementedJinaExecutorSnapshotProgressServer
// for forward compatibility
type JinaExecutorSnapshotProgressServer interface {
	SnapshotStatus(context.Context, *SnapshotId) (*SnapshotStatusProto, error)
	mustEmbedUnimplementedJinaExecutorSnapshotProgressServer()
}

// UnimplementedJinaExecutorSnapshotProgressServer must be embedded to have forward compatible implementations.
type UnimplementedJinaExecutorSnapshotProgressServer struct {
}

func (UnimplementedJinaExecutorSnapshotProgressServer) SnapshotStatus(context.Context, *SnapshotId) (*SnapshotStatusProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SnapshotStatus not implemented")
}
func (UnimplementedJinaExecutorSnapshotProgressServer) mustEmbedUnimplementedJinaExecutorSnapshotProgressServer() {
}

// UnsafeJinaExecutorSnapshotProgressServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaExecutorSnapshotProgressServer will
// result in compilation errors.
type UnsafeJinaExecutorSnapshotProgressServer interface {
	mustEmbedUnimplementedJinaExecutorSnapshotProgressServer()
}

func RegisterJinaExecutorSnapshotProgressServer(s grpc.ServiceRegistrar, srv JinaExecutorSnapshotProgressServer) {
	s.RegisterService(&JinaExecutorSnapshotProgress_ServiceDesc, srv)
}

func _JinaExecutorSnapshotProgress_SnapshotStatus_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(SnapshotId)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaExecutorSnapshotProgressServer).SnapshotStatus(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaExecutorSnapshotProgress/snapshot_status",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaExecutorSnapshotProgressServer).SnapshotStatus(ctx, req.(*SnapshotId))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaExecutorSnapshotProgress_ServiceDesc is the grpc.ServiceDesc for JinaExecutorSnapshotProgress service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaExecutorSnapshotProgress_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaExecutorSnapshotProgress",
	HandlerType: (*JinaExecutorSnapshotProgressServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "snapshot_status",
			Handler:    _JinaExecutorSnapshotProgress_SnapshotStatus_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaExecutorRestoreClient is the client API for JinaExecutorRestore service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaExecutorRestoreClient interface {
	Restore(ctx context.Context, in *RestoreSnapshotCommand, opts ...grpc.CallOption) (*RestoreSnapshotStatusProto, error)
}

type jinaExecutorRestoreClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaExecutorRestoreClient(cc grpc.ClientConnInterface) JinaExecutorRestoreClient {
	return &jinaExecutorRestoreClient{cc}
}

func (c *jinaExecutorRestoreClient) Restore(ctx context.Context, in *RestoreSnapshotCommand, opts ...grpc.CallOption) (*RestoreSnapshotStatusProto, error) {
	out := new(RestoreSnapshotStatusProto)
	err := c.cc.Invoke(ctx, "/jina.JinaExecutorRestore/restore", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaExecutorRestoreServer is the server API for JinaExecutorRestore service.
// All implementations must embed UnimplementedJinaExecutorRestoreServer
// for forward compatibility
type JinaExecutorRestoreServer interface {
	Restore(context.Context, *RestoreSnapshotCommand) (*RestoreSnapshotStatusProto, error)
	mustEmbedUnimplementedJinaExecutorRestoreServer()
}

// UnimplementedJinaExecutorRestoreServer must be embedded to have forward compatible implementations.
type UnimplementedJinaExecutorRestoreServer struct {
}

func (UnimplementedJinaExecutorRestoreServer) Restore(context.Context, *RestoreSnapshotCommand) (*RestoreSnapshotStatusProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Restore not implemented")
}
func (UnimplementedJinaExecutorRestoreServer) mustEmbedUnimplementedJinaExecutorRestoreServer() {}

// UnsafeJinaExecutorRestoreServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaExecutorRestoreServer will
// result in compilation errors.
type UnsafeJinaExecutorRestoreServer interface {
	mustEmbedUnimplementedJinaExecutorRestoreServer()
}

func RegisterJinaExecutorRestoreServer(s grpc.ServiceRegistrar, srv JinaExecutorRestoreServer) {
	s.RegisterService(&JinaExecutorRestore_ServiceDesc, srv)
}

func _JinaExecutorRestore_Restore_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RestoreSnapshotCommand)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaExecutorRestoreServer).Restore(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaExecutorRestore/restore",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaExecutorRestoreServer).Restore(ctx, req.(*RestoreSnapshotCommand))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaExecutorRestore_ServiceDesc is the grpc.ServiceDesc for JinaExecutorRestore service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaExecutorRestore_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaExecutorRestore",
	HandlerType: (*JinaExecutorRestoreServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "restore",
			Handler:    _JinaExecutorRestore_Restore_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}

// JinaExecutorRestoreProgressClient is the client API for JinaExecutorRestoreProgress service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type JinaExecutorRestoreProgressClient interface {
	RestoreStatus(ctx context.Context, in *RestoreId, opts ...grpc.CallOption) (*RestoreSnapshotStatusProto, error)
}

type jinaExecutorRestoreProgressClient struct {
	cc grpc.ClientConnInterface
}

func NewJinaExecutorRestoreProgressClient(cc grpc.ClientConnInterface) JinaExecutorRestoreProgressClient {
	return &jinaExecutorRestoreProgressClient{cc}
}

func (c *jinaExecutorRestoreProgressClient) RestoreStatus(ctx context.Context, in *RestoreId, opts ...grpc.CallOption) (*RestoreSnapshotStatusProto, error) {
	out := new(RestoreSnapshotStatusProto)
	err := c.cc.Invoke(ctx, "/jina.JinaExecutorRestoreProgress/restore_status", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// JinaExecutorRestoreProgressServer is the server API for JinaExecutorRestoreProgress service.
// All implementations must embed UnimplementedJinaExecutorRestoreProgressServer
// for forward compatibility
type JinaExecutorRestoreProgressServer interface {
	RestoreStatus(context.Context, *RestoreId) (*RestoreSnapshotStatusProto, error)
	mustEmbedUnimplementedJinaExecutorRestoreProgressServer()
}

// UnimplementedJinaExecutorRestoreProgressServer must be embedded to have forward compatible implementations.
type UnimplementedJinaExecutorRestoreProgressServer struct {
}

func (UnimplementedJinaExecutorRestoreProgressServer) RestoreStatus(context.Context, *RestoreId) (*RestoreSnapshotStatusProto, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RestoreStatus not implemented")
}
func (UnimplementedJinaExecutorRestoreProgressServer) mustEmbedUnimplementedJinaExecutorRestoreProgressServer() {
}

// UnsafeJinaExecutorRestoreProgressServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to JinaExecutorRestoreProgressServer will
// result in compilation errors.
type UnsafeJinaExecutorRestoreProgressServer interface {
	mustEmbedUnimplementedJinaExecutorRestoreProgressServer()
}

func RegisterJinaExecutorRestoreProgressServer(s grpc.ServiceRegistrar, srv JinaExecutorRestoreProgressServer) {
	s.RegisterService(&JinaExecutorRestoreProgress_ServiceDesc, srv)
}

func _JinaExecutorRestoreProgress_RestoreStatus_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RestoreId)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(JinaExecutorRestoreProgressServer).RestoreStatus(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/jina.JinaExecutorRestoreProgress/restore_status",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(JinaExecutorRestoreProgressServer).RestoreStatus(ctx, req.(*RestoreId))
	}
	return interceptor(ctx, in, info, handler)
}

// JinaExecutorRestoreProgress_ServiceDesc is the grpc.ServiceDesc for JinaExecutorRestoreProgress service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var JinaExecutorRestoreProgress_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "jina.JinaExecutorRestoreProgress",
	HandlerType: (*JinaExecutorRestoreProgressServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "restore_status",
			Handler:    _JinaExecutorRestoreProgress_RestoreStatus_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "jina.proto",
}
