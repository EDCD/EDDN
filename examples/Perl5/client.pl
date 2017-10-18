#!/usr/bin/env perl

use JSON::XS 'decode_json';
use ZMQ::FFI qw(ZMQ_SUB);
use Time::HiRes q(usleep);
use Compress::Zlib;

sub msg {
  printf STDERR @_;
}

my $endpoint = "tcp://eddn.edcd.io:9500";
my $ctx      = ZMQ::FFI->new();

my $s = $ctx->socket(ZMQ_SUB);

$s->connect($endpoint);

$s->subscribe('');
while(1)
{
  usleep 100_000 until ($s->has_pollin);
  my $data = $s->recv();

  # turn the json into a perl hash
  my $pj = decode_json(uncompress($data));
  my $schema = $pj->{'$schemaRef'};
  msg "schema = %s\n", $schema;
  msg "  software = %s\n", $pj->{header}->{softwareName};
  if ($schema eq "https://eddn.edcd.io/schemas/journal/1") {
    my $event = $pj->{message}->{event};
    if ($event eq "FSDJump") {
      msg "  StarSystem = %s\n", $pj->{message}->{StarSystem};
    }
  }
  msg "------\n";
}
$s->unsubscribe('');
